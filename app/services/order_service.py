from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.fcm import send_push
from app.models.notification import Notification
from app.models.order import (
    DELIVERY_CHARGE_MULTIPLE,
    DELIVERY_CHARGE_SINGLE,
    Order,
    OrderItem,
    OrderStatus,
)
from app.models.order_tracking import OrderTracking
from app.models.product import CategoryType
from app.repositories.address_repository import AddressRepository
from app.repositories.cart_repository import CartRepository
from app.repositories.notification_repository import DeviceTokenRepository, NotificationRepository
from app.repositories.offer_repository import OfferRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.order import AdminOrderCancel, OrderCreate, OrderStatusUpdate

VEGETABLE_ORDER_START_HOUR = 5  # 5 AM UTC
VEGETABLE_ORDER_END_HOUR = 9    # 9 AM UTC


class OrderService:
    """Complete order lifecycle business logic."""

    def __init__(self, db: AsyncSession) -> None:
        self.order_repo = OrderRepository(db)
        self.cart_repo = CartRepository(db)
        self.product_repo = ProductRepository(db)
        self.offer_repo = OfferRepository(db)
        self.address_repo = AddressRepository(db)
        self.notif_repo = NotificationRepository(db)
        self.device_repo = DeviceTokenRepository(db)

    # ── Order creation ────────────────────────────────────────────────────────

    async def create_order(self, user_id: UUID, payload: OrderCreate) -> Order:
        """Create an order from the user's current cart.

        Steps:
        1. Validate cart is non-empty
        2. Resolve delivery address
        3. Enforce vegetable order time window (5–9 AM UTC)
        4. Validate stock per item
        5. Apply active offer discount per item
        6. Calculate delivery charge (single item: 10, multiple: 15)
        7. Persist order + order items
        8. Deduct stock (auto-flag out-of-stock)
        9. Bulk-clear cart
        10. Insert first tracking event (PLACED)
        11. Send order confirmation notification
        """
        cart = await self.cart_repo.get_by_user_id(user_id)
        if not cart or not cart.items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cart is empty",
            )

        # ── Resolve delivery address ─────────────────────────────────────────
        delivery_address = payload.delivery_address
        if payload.address_id:
            address = await self.address_repo.get_by_user_and_id(user_id, payload.address_id)
            if not address:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Delivery address not found",
                )
            delivery_address = (
                f"{address.street}, {address.city}, {address.state} - {address.pincode}"
            )

        # ── Vegetable time-window check ──────────────────────────────────────
        now_utc = datetime.now(timezone.utc)
        for item in cart.items:
            product = await self.product_repo.get_with_category(item.product_id)
            if product and product.category and product.category.type == CategoryType.VEGETABLE:
                if not (VEGETABLE_ORDER_START_HOUR <= now_utc.hour < VEGETABLE_ORDER_END_HOUR):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Vegetable orders are only accepted between 5 AM and 9 AM UTC",
                    )

        # ── Stock validation, offer application, build order items ───────────
        order_items: list[OrderItem] = []
        subtotal = 0.0

        for cart_item in cart.items:
            product = await self.product_repo.get_by_id(cart_item.product_id)
            if not product or not product.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="One or more products are no longer available",
                )
            if product.is_out_of_stock or product.stock < cart_item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock for '{product.name}'",
                )

            unit_price = float(product.price)

            # Apply active offer if available and within usage cap
            offer = await self.offer_repo.get_active_for_product(product.id)
            if offer and (offer.max_uses is None or offer.used_count < offer.max_uses):
                discount = unit_price * (float(offer.discount_percent) / 100)
                unit_price = round(unit_price - discount, 2)
                await self.offer_repo.update(offer, {"used_count": offer.used_count + 1})

            item_subtotal = round(unit_price * cart_item.quantity, 2)
            subtotal = round(subtotal + item_subtotal, 2)
            order_items.append(
                OrderItem(
                    product_id=product.id,
                    quantity=cart_item.quantity,
                    unit_price=unit_price,
                    subtotal=item_subtotal,
                )
            )

        # ── Delivery charge ──────────────────────────────────────────────────
        delivery_charge = (
            DELIVERY_CHARGE_SINGLE if len(cart.items) == 1 else DELIVERY_CHARGE_MULTIPLE
        )
        total = round(subtotal + delivery_charge, 2)

        # ── Persist order ────────────────────────────────────────────────────
        order = Order(
            user_id=user_id,
            subtotal=subtotal,
            delivery_charge=delivery_charge,
            total=total,
            delivery_address=delivery_address,
            notes=payload.notes,
        )
        order.items = order_items
        await self.order_repo.create(order)

        # ── Deduct stock ─────────────────────────────────────────────────────
        for cart_item in cart.items:
            product = await self.product_repo.get_by_id(cart_item.product_id)
            new_stock = product.stock - cart_item.quantity
            await self.product_repo.update(
                product,
                {"stock": new_stock, "is_out_of_stock": new_stock <= 0},
            )

        # ── Clear cart (bulk DELETE) ─────────────────────────────────────────
        await self.cart_repo.clear_items(cart.id)

        # ── Initial tracking event ───────────────────────────────────────────
        tracking = OrderTracking(
            order_id=order.id,
            status=OrderStatus.PLACED,
            description="Order placed successfully",
            changed_by="system",
        )
        self.order_repo.db.add(tracking)

        # ── Confirmation notification ────────────────────────────────────────
        notif = Notification(
            user_id=user_id,
            title="Order Placed",
            body=f"Your order #{order.id} has been placed. Total: ₹{total}",
        )
        self.notif_repo.db.add(notif)

        await self.order_repo.db.flush()
        # ── FCM push: user confirmation + admin alert ──────────────────────
        user_tokens = await self.device_repo.get_tokens_for_user(user_id)
        await send_push(user_tokens, "Order Placed ✅", f"Your order #{order.id} was placed. Total: ₹{total}")

        admin_tokens = await self.device_repo.get_all_admin_tokens()
        await send_push(admin_tokens, "New Order Received 🛎️", f"New order received: Order #{order.id}")
        return await self.order_repo.get_full(order.id)

    # ── Customer queries ──────────────────────────────────────────────────────

    async def get_order(self, order_id: UUID, user_id: UUID) -> Order:
        """Return an order (with items and tracking) for the owning user."""
        order = await self.order_repo.get_full(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
            )
        if order.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
            )
        return order

    async def list_user_orders(self, user_id: UUID, skip: int = 0, limit: int = 20):
        """Return paginated orders for the authenticated user."""
        return await self.order_repo.list_by_user(user_id, skip, limit)

    # ── Admin operations ──────────────────────────────────────────────────────

    async def admin_get_order(self, order_id: UUID) -> Order:
        """Admin: fetch any order with full detail."""
        order = await self.order_repo.get_full(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
            )
        return order

    async def admin_list_orders(self, skip: int = 0, limit: int = 30):
        """Admin: paginated list of all orders."""
        return await self.order_repo.list_all_orders(skip, limit)

    async def admin_cancel_order(self, order_id: UUID, payload: AdminOrderCancel) -> Order:
        """Admin: cancel an order and notify the customer."""
        order = await self.order_repo.get_full(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
            )
        if order.status in (OrderStatus.DELIVERED, OrderStatus.CANCELLED):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel an order with status '{order.status.value}'",
            )

        # Restore stock for all items in the cancelled order
        for order_item in order.items:
            product = await self.product_repo.get_by_id(order_item.product_id)
            if product:
                restored_stock = product.stock + order_item.quantity
                await self.product_repo.update(
                    product,
                    {"stock": restored_stock, "is_out_of_stock": restored_stock <= 0},
                )

        await self.order_repo.update(
            order, {"status": OrderStatus.CANCELLED, "cancel_reason": payload.reason}
        )

        tracking = OrderTracking(
            order_id=order.id,
            status=OrderStatus.CANCELLED,
            description=payload.reason,
            changed_by="admin",
        )
        self.order_repo.db.add(tracking)

        notif = Notification(
            user_id=order.user_id,
            title="Order Cancelled",
            body=f"Your order #{order.id} was cancelled. Reason: {payload.reason}",
        )
        self.notif_repo.db.add(notif)
        await self.order_repo.db.flush()

        # FCM push to customer
        tokens = await self.device_repo.get_tokens_for_user(order.user_id)
        await send_push(tokens, "Order Cancelled ❌", f"Your order #{order.id} was cancelled. Reason: {payload.reason}")

        return await self.order_repo.get_full(order.id)

    async def admin_update_status(
        self, order_id: UUID, payload: OrderStatusUpdate
    ) -> Order:
        """Admin: advance the order to a new status and record a tracking event."""
        order = await self.order_repo.get_full(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
            )
        if order.status == OrderStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot update a cancelled order",
            )

        # If changing status to CANCELLED, restore stock
        if payload.status == OrderStatus.CANCELLED:
            for order_item in order.items:
                product = await self.product_repo.get_by_id(order_item.product_id)
                if product:
                    restored_stock = product.stock + order_item.quantity
                    await self.product_repo.update(
                        product,
                        {"stock": restored_stock, "is_out_of_stock": restored_stock <= 0},
                    )

        await self.order_repo.update(order, {"status": payload.status})

        tracking = OrderTracking(
            order_id=order.id,
            status=payload.status,
            description=payload.description,
            changed_by="admin",
        )
        self.order_repo.db.add(tracking)

        notif = Notification(
            user_id=order.user_id,
            title="Order Update",
            body=f"Your order #{order.id} status is now: {payload.status.value}.",
        )
        self.notif_repo.db.add(notif)
        await self.order_repo.db.flush()

        # FCM push with status-specific message
        status_messages = {
            OrderStatus.CONFIRMED:        ("Order Confirmed ✅",        f"Your order #{order.id} has been confirmed!"),
            OrderStatus.PACKED:           ("Order Packed 📦",           f"Your order #{order.id} is packed and ready."),
            OrderStatus.OUT_FOR_DELIVERY: ("Out for Delivery 🚚",       f"Your order #{order.id} is on its way!"),
            OrderStatus.DELIVERED:        ("Order Delivered 🎉",        f"Your order #{order.id} has been delivered!"),
            OrderStatus.CANCELLED:        ("Order Cancelled ❌",        f"Your order #{order.id} was cancelled."),
        }
        title, body = status_messages.get(
            payload.status,
            ("Order Update", f"Your order #{order.id} is now: {payload.status.value}.")
        )
        tokens = await self.device_repo.get_tokens_for_user(order.user_id)
        await send_push(tokens, title, body)

        return await self.order_repo.get_full(order.id)
