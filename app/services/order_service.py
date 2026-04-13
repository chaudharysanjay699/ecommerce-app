from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.fcm import send_push
from app.models.notification import Notification
from app.models.order import (
    Order,
    OrderItem,
    OrderStatus,
)
from app.models.order_tracking import OrderTracking
from app.models.product import CategoryType
from app.repositories.address_repository import AddressRepository
from app.repositories.app_settings_repository import AppSettingsRepository
from app.repositories.cart_repository import CartRepository
from app.repositories.notification_repository import DeviceTokenRepository, NotificationRepository
from app.repositories.offer_repository import OfferRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.user_repository import UserRepository
from app.schemas.order import AdminOrderCancel, OrderCreate, OrderStatusUpdate
from app.services.email_service import send_admin_order_email, send_invoice_email, send_low_stock_alert_email

logger = logging.getLogger(__name__)


class OrderService:
    """Complete order lifecycle business logic."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.order_repo = OrderRepository(db)
        self.cart_repo = CartRepository(db)
        self.product_repo = ProductRepository(db)
        self.offer_repo = OfferRepository(db)
        self.address_repo = AddressRepository(db)
        self.notif_repo = NotificationRepository(db)
        self.device_repo = DeviceTokenRepository(db)
        self.user_repo = UserRepository(db)
        self.settings_repo = AppSettingsRepository(db)

    # ── Order creation ────────────────────────────────────────────────────────

    async def create_order(self, user_id: UUID, payload: OrderCreate) -> Order:
        """Create an order from the user's current cart.

        Steps:
        1. Check maintenance mode
        2. Check daily order limit (if enabled)
        3. Validate cart is non-empty
        4. Resolve delivery address
        5. Enforce vegetable order time window (from DB settings)
        6. Validate stock per item
        7. Apply active offer discount per item
        8. Calculate delivery charge (from DB settings)
        9. Persist order + order items
        10. Deduct stock (auto-flag out-of-stock)
        11. Bulk-clear cart
        12. Insert first tracking event (PLACED)
        13. Send order confirmation notification
        """
        # ── Check daily order limit ──────────────────────────────────────────
        settings = await self.settings_repo.get_settings()

        # ── Maintenance mode check ───────────────────────────────────────────
        if settings.maintenance_mode:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=settings.maintenance_message,
            )

        if settings.order_limit_enabled and settings.daily_order_limit is not None:
            # Count orders placed today
            today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            result = await self.db.execute(
                select(func.count())
                .select_from(Order)
                .where(Order.created_at >= today_start)
            )
            today_orders_count = result.scalar_one()
            
            if today_orders_count >= settings.daily_order_limit:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=settings.order_limit_message,
                )
        
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
        if settings.veg_order_enabled:
            # Convert UTC to IST (UTC + 5:30)
            from datetime import timedelta
            ist_offset = timedelta(hours=5, minutes=30)
            now_ist = now_utc + ist_offset
            ist_hour = now_ist.hour
            
            for item in cart.items:
                product = await self.product_repo.get_with_category(item.product_id)
                if product and product.category and product.category.type == CategoryType.VEGETABLE:
                    # Allow orders ONLY between 5 AM and 9 AM IST
                    if not (settings.veg_order_start_hour <= ist_hour < settings.veg_order_end_hour):
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Vegetable orders are only accepted between {settings.veg_order_start_hour}:00 and {settings.veg_order_end_hour}:00 AM IST. Please place your order during this time window.",
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
            item_discount = 0.0
            offer = await self.offer_repo.get_active_for_product(product.id)
            if offer and (offer.max_uses is None or offer.used_count < offer.max_uses):
                item_discount = round(unit_price * (float(offer.discount_percent) / 100), 2)
                unit_price = round(unit_price - item_discount, 2)
                await self.offer_repo.update(offer, {"used_count": offer.used_count + 1})

            # GST per line item
            gst_rate = float(getattr(product, "gst_rate", 0) or 0)
            if gst_rate == 0:
                gst_rate = float(getattr(settings, "default_tax_rate", 0) or 0)
            item_taxable = round(unit_price * cart_item.quantity, 2)
            tax_amount = round(item_taxable * gst_rate / 100, 2) if gst_rate else 0.0
            item_subtotal = round(item_taxable + tax_amount, 2)

            subtotal = round(subtotal + item_subtotal, 2)
            order_items.append(
                OrderItem(
                    product_id=product.id,
                    quantity=cart_item.quantity,
                    unit_price=unit_price,
                    discount=item_discount,
                    tax_rate=gst_rate,
                    tax_amount=tax_amount,
                    hsn_code=getattr(product, "hsn_code", None),
                    subtotal=item_subtotal,
                )
            )

        # ── Delivery charge ──────────────────────────────────────────────────
        delivery_charge = 0.0
        tiers = getattr(settings, "delivery_charge_tiers", None)
        if tiers and isinstance(tiers, list) and len(tiers) > 0:
            # Find the first tier where subtotal is within min/max
            for tier in tiers:
                min_price = float(tier.get("min_price", 0))
                max_price = tier.get("max_price")
                max_price = float(max_price) if max_price is not None else None
                if subtotal >= min_price and (max_price is None or subtotal <= max_price):
                    delivery_charge = float(tier.get("delivery_charge", 0))
                    break
        else:
            delivery_charge = (
                float(settings.delivery_charge_single) if len(cart.items) == 1
                else float(settings.delivery_charge_multiple)
            )
        total = round(subtotal + delivery_charge, 2)

        # ── Generate invoice number ────────────────────────────────────────
        invoice_prefix = getattr(settings, "invoice_prefix", "INV") or "INV"
        invoice_number = await self.order_repo.generate_invoice_number(invoice_prefix)

        # ── Persist order ────────────────────────────────────────────────────
        order = Order(
            user_id=user_id,
            subtotal=subtotal,
            delivery_charge=delivery_charge,
            total=total,
            delivery_address=delivery_address,
            notes=payload.notes,
            invoice_number=invoice_number,
        )
        order.items = order_items
        await self.order_repo.create(order)

        # ── Deduct stock ─────────────────────────────────────────────────────
        low_stock_items = []
        low_stock_threshold = getattr(settings, "low_stock_threshold", 5)
        low_stock_alert_enabled = getattr(settings, "low_stock_alert_enabled", True)

        for cart_item in cart.items:
            product = await self.product_repo.get_by_id(cart_item.product_id)
            new_stock = product.stock - cart_item.quantity
            await self.product_repo.update(
                product,
                {"stock": new_stock, "is_out_of_stock": new_stock <= 0},
            )
            if low_stock_alert_enabled and new_stock <= low_stock_threshold:
                low_stock_items.append({
                    "name": product.name,
                    "stock": max(new_stock, 0),
                })

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
            order_id=order.id,
        )
        self.notif_repo.db.add(notif)

        await self.order_repo.db.flush()

        # ── Gather data needed for background tasks (while DB session is alive) ──
        user_tokens = await self.device_repo.get_tokens_for_user(user_id)
        admin_tokens = await self.device_repo.get_all_admin_tokens()
        user = await self.user_repo.get_by_id(user_id)
        user_email = user.email if user else None
        admin_emails = await self.user_repo.get_admin_emails()
        full_order = await self.order_repo.get_full(order.id)
        store_name = settings.store_name
        order_id = order.id

        # ── Fire background tasks (FCM, PDFs, emails) ───────────────────────
        async def _post_order_tasks():
            try:
                # FCM push: user confirmation + admin alert
                await send_push(user_tokens, "Order Placed ✅", f"Your order #{order_id} was placed. Total: ₹{total}")
                await send_push(admin_tokens, "New Order Received 🛎️", f"New order received: Order #{order_id}")

                # Generate invoice & shipping label PDFs
                try:
                    from app.services.pdf_service import generate_invoice_pdf, generate_shipping_label_pdf
                    from app.core.database import AsyncSessionLocal

                    invoice_url = await generate_invoice_pdf(full_order, store_name=store_name, app_settings=settings)
                    label_url = await generate_shipping_label_pdf(full_order, store_name=store_name)
                    # Update order with PDF URLs in a fresh DB session
                    async with AsyncSessionLocal() as bg_db:
                        from sqlalchemy import update as sa_update
                        from app.models.order import Order as OrderModel
                        await bg_db.execute(
                            sa_update(OrderModel)
                            .where(OrderModel.id == order_id)
                            .values(invoice_url=invoice_url, shipping_label_url=label_url)
                        )
                        await bg_db.commit()
                except Exception:
                    logger.exception("Failed to generate PDFs for order %s", order_id)

                # Send invoice email to customer
                if user_email:
                    await send_invoice_email(user_email, full_order, store_name=store_name)

                # Send admin email notification
                await send_admin_order_email(admin_emails, full_order, event="New Order Placed", store_name=store_name)

                # Send low stock alert email to admins
                if low_stock_items:
                    await send_low_stock_alert_email(admin_emails, low_stock_items, store_name=store_name)
            except Exception:
                logger.exception("Background post-order tasks failed for order %s", order_id)

        asyncio.create_task(_post_order_tasks())

        return full_order

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

    async def cancel_order(self, order_id: UUID, user_id: UUID, reason: str) -> Order:
        """Customer: cancel own order (allowed before out_for_delivery)."""
        order = await self.order_repo.get_full(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
            )
        if order.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
            )

        cancellable = (
            OrderStatus.PLACED,
            OrderStatus.CONFIRMED,
            OrderStatus.PACKED,
        )
        if order.status not in cancellable:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Order cannot be cancelled once it is '{order.status.value}'",
            )

        # Restore stock
        for order_item in order.items:
            product = await self.product_repo.get_by_id(order_item.product_id)
            if product:
                restored_stock = product.stock + order_item.quantity
                await self.product_repo.update(
                    product,
                    {"stock": restored_stock, "is_out_of_stock": restored_stock <= 0},
                )

        await self.order_repo.update(
            order, {"status": OrderStatus.CANCELLED, "cancel_reason": reason}
        )

        tracking = OrderTracking(
            order_id=order.id,
            status=OrderStatus.CANCELLED,
            description=f"Cancelled by customer: {reason}",
            changed_by="customer",
        )
        self.order_repo.db.add(tracking)

        notif = Notification(
            user_id=user_id,
            title="Order Cancelled",
            body=f"Your order #{order.id} has been cancelled.",
            order_id=order.id,
        )
        self.notif_repo.db.add(notif)
        await self.order_repo.db.flush()

        # Gather data for background tasks
        tokens = await self.device_repo.get_tokens_for_user(user_id)
        full_order = await self.order_repo.get_full(order.id)
        admin_emails = await self.user_repo.get_admin_emails()
        app_settings = await self.settings_repo.get_settings()
        admin_tokens = await self.device_repo.get_all_admin_tokens()
        _order_id = order.id

        async def _post_cancel_tasks():
            try:
                await send_push(tokens, "Order Cancelled", f"Your order #{_order_id} has been cancelled.")
                await send_admin_order_email(
                    admin_emails, full_order, event="Order Cancelled by Customer",
                    store_name=app_settings.store_name,
                )
                await send_push(
                    admin_tokens, "Order Cancelled by Customer",
                    f"Order #{_order_id} was cancelled by the customer. Reason: {reason}",
                )
            except Exception:
                logger.exception("Background cancel tasks failed for order %s", _order_id)

        asyncio.create_task(_post_cancel_tasks())

        return full_order

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
        if order.user and order.user.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot change status — user account has been deleted",
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
            order_id=order.id,
        )
        self.notif_repo.db.add(notif)
        await self.order_repo.db.flush()

        # Gather data for background tasks
        tokens = await self.device_repo.get_tokens_for_user(order.user_id)
        full_order = await self.order_repo.get_full(order.id)
        admin_emails = await self.user_repo.get_admin_emails()
        app_settings = await self.settings_repo.get_settings()
        _order_id = order.id
        _reason = payload.reason

        async def _post_admin_cancel_tasks():
            try:
                await send_push(tokens, "Order Cancelled ❌", f"Your order #{_order_id} was cancelled. Reason: {_reason}")
                await send_admin_order_email(admin_emails, full_order, event="Order Cancelled", store_name=app_settings.store_name)
            except Exception:
                logger.exception("Background admin-cancel tasks failed for order %s", _order_id)

        asyncio.create_task(_post_admin_cancel_tasks())

        return full_order

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
        if order.user and order.user.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot change status — user account has been deleted",
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
            order_id=order.id,
        )
        self.notif_repo.db.add(notif)
        await self.order_repo.db.flush()

        # Gather data for background tasks
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
        full_order = await self.order_repo.get_full(order.id)
        app_settings = await self.settings_repo.get_settings()
        customer = await self.user_repo.get_by_id(order.user_id)
        customer_email = customer.email if customer else None
        admin_emails = await self.user_repo.get_admin_emails() if payload.status == OrderStatus.DELIVERED else []
        _order_id = order.id
        _status = payload.status

        async def _post_status_update_tasks():
            try:
                await send_push(tokens, title, body)

                if customer_email:
                    from app.services.email_service import send_order_status_email
                    await send_order_status_email(
                        customer_email, full_order,
                        event=f"Order Status: {_status.value.replace('_', ' ').title()}",
                        store_name=app_settings.store_name,
                    )

                if _status == OrderStatus.DELIVERED and admin_emails:
                    await send_admin_order_email(
                        admin_emails, full_order,
                        event="Order Delivered",
                        store_name=app_settings.store_name,
                    )
            except Exception:
                logger.exception("Background status-update tasks failed for order %s", _order_id)

        asyncio.create_task(_post_status_update_tasks())

        return full_order
