from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cart import Cart, CartItem
from app.repositories.cart_repository import CartItemRepository, CartRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.offer_repository import OfferRepository
from app.schemas.cart import CartItemAdd, CartItemUpdate


class CartService:
    """Business logic for the shopping cart."""

    def __init__(self, db: AsyncSession) -> None:
        self.cart_repo = CartRepository(db)
        self.item_repo = CartItemRepository(db)
        self.product_repo = ProductRepository(db)
        self.offer_repo = OfferRepository(db)

    async def _get_or_create_cart(self, user_id: UUID) -> Cart:
        cart = await self.cart_repo.get_by_user_id(user_id)
        if not cart:
            cart = Cart(user_id=user_id)
            cart = await self.cart_repo.create(cart)
        return cart

    async def get_cart(self, user_id: UUID) -> Cart:
        """Retrieve (or lazily create) the user's cart."""
        return await self._get_or_create_cart(user_id)

    async def add_item(self, user_id: UUID, payload: CartItemAdd) -> Cart:
        """Add a product to the cart; accumulates quantity if already present."""
        product = await self.product_repo.get_by_id(payload.product_id)
        if not product or not product.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
            )
        if product.is_out_of_stock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product is out of stock",
            )
        if product.stock < payload.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Only {product.stock} unit(s) available",
            )

        cart = await self._get_or_create_cart(user_id)
        existing = await self.item_repo.get_by_cart_and_product(cart.id, payload.product_id)

        # Check for active offer and calculate final price
        active_offer = await self.offer_repo.get_active_for_product(payload.product_id)
        final_price = float(product.price)
        if active_offer:
            final_price = float(product.price) * (1 - float(active_offer.discount_percent) / 100)

        if existing:
            # Update both quantity and unit_price (in case offer changed)
            await self.item_repo.update(
                existing, 
                {"quantity": existing.quantity + payload.quantity, "unit_price": final_price}
            )
        else:
            new_item = CartItem(
                cart_id=cart.id,
                product_id=payload.product_id,
                quantity=payload.quantity,
                unit_price=final_price,
            )
            await self.item_repo.create(new_item)

        # Expire cart so selectinload re-populates items from DB
        self.cart_repo.db.expire(cart)
        return await self.cart_repo.get_by_user_id(user_id)

    async def update_item(
        self, user_id: UUID, product_id: UUID, payload: CartItemUpdate
    ) -> Cart:
        """Set the exact quantity for a cart item."""
        cart = await self.cart_repo.get_by_user_id(user_id)
        if not cart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Cart is empty"
            )
        item = await self.item_repo.get_by_cart_and_product(cart.id, product_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Item not in cart"
            )
        await self.item_repo.update(item, {"quantity": payload.quantity})
        # Expire cart so selectinload re-populates items from DB
        self.cart_repo.db.expire(cart)
        return await self.cart_repo.get_by_user_id(user_id)

    async def remove_item(self, user_id: UUID, product_id: UUID) -> Cart:
        """Remove a single product from the cart."""
        cart = await self.cart_repo.get_by_user_id(user_id)
        if not cart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Cart is empty"
            )
        item = await self.item_repo.get_by_cart_and_product(cart.id, product_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Item not in cart"
            )
        await self.item_repo.delete(item)
        # Expire cart so selectinload re-populates items from DB
        self.cart_repo.db.expire(cart)
        return await self.cart_repo.get_by_user_id(user_id)

    async def clear_cart(self, user_id: UUID) -> None:
        """Remove all items from the cart in a single bulk DELETE."""
        cart = await self.cart_repo.get_by_user_id(user_id)
        if cart:
            await self.cart_repo.clear_items(cart.id)
