from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.fcm import send_push
from app.models.notification import Notification
from app.models.product import Category, Product
from app.repositories.notification_repository import DeviceTokenRepository, NotificationRepository
from app.repositories.product_repository import CategoryRepository, ProductRepository
from app.repositories.user_repository import UserRepository
from app.schemas.product import CategoryCreate, CategoryUpdate, ProductCreate, ProductUpdate, StockAdjust


class CategoryService:
    """Business logic for product categories."""

    def __init__(self, db: AsyncSession) -> None:
        self.repo = CategoryRepository(db)

    async def list_active(self, skip: int = 0, limit: int = 100):
        """Return all active categories (all levels)."""
        return await self.repo.list_active(skip, limit)

    async def list_top_level(self, skip: int = 0, limit: int = 100):
        """Return active top-level (parent) categories only."""
        return await self.repo.list_top_level_active(skip, limit)

    async def list_nav(self):
        """Return categories shown in the bottom navigation bar."""
        return await self.repo.list_nav()

    async def list_with_children(self):
        """Return all top-level categories with their subcategories (admin)."""
        return await self.repo.list_with_children()

    async def list_children(self, parent_id: UUID):
        """Return subcategories of a given parent."""
        return await self.repo.list_children(parent_id)

    async def get_category(self, category_id: UUID) -> Category:
        """Return a single category or raise 404."""
        category = await self.repo.get_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
            )
        return category

    async def create(self, payload: CategoryCreate) -> Category:
        """Admin: create a new category. Raises 409 on duplicate slug."""
        if await self.repo.get_by_slug(payload.slug):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Category slug already exists",
            )
        category = Category(**payload.model_dump())
        return await self.repo.create(category)

    async def update(self, category_id: UUID, payload: CategoryUpdate) -> Category:
        """Admin: partially update a category."""
        category = await self.repo.get_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
            )
        data = payload.model_dump(exclude_none=True)
        if not data:
            return category
        if "slug" in data and data["slug"] != category.slug:
            if await self.repo.get_by_slug(data["slug"]):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Category slug already exists",
                )
        return await self.repo.update(category, data)

    async def toggle_status(self, category_id: UUID) -> Category:
        """Admin: toggle is_active on a category."""
        category = await self.repo.get_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
            )
        return await self.repo.update(category, {"is_active": not category.is_active})


class ProductService:
    """Business logic for products and inventory."""

    def __init__(self, db: AsyncSession) -> None:
        self.repo = ProductRepository(db)
        self.user_repo = UserRepository(db)
        self.notif_repo = NotificationRepository(db)
        self.device_repo = DeviceTokenRepository(db)

    async def get_product(self, product_id: UUID) -> Product:
        """Return a single product or raise 404."""
        product = await self.repo.get_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
            )
        return product

    async def get_detail(self, product_id: UUID) -> Product:
        """Return a product with its category eagerly loaded."""
        product = await self.repo.get_with_category(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
            )
        return product

    async def list_products_with_category(
        self,
        category_id: UUID | None = None,
        search: str | None = None,
        skip: int = 0,
        limit: int = 30,
        sort_by: str | None = None,
    ):
        """Return active products with nested category, supports filters and sorting."""
        from app.schemas.product import ProductDetailOut
        # If search is used, fallback to flat search (no category eager loading)
        if search:
            products = await self.repo.search(search, skip, limit)
            # Manually load category for each product (inefficient, but needed for search)
            from app.repositories.product_repository import CategoryRepository
            categories = {}
            db = self.repo.db
            cat_repo = CategoryRepository(db)
            result = []
            for p in products:
                if p.category_id not in categories:
                    categories[p.category_id] = await cat_repo.get_by_id(p.category_id)
                # Build a SQLAlchemy object with .category set
                p.category = categories[p.category_id]
                result.append(ProductDetailOut.model_validate(p, from_attributes=True))
            return result
        if category_id:
            if sort_by == "popular":
                products = await self.repo.list_popular_by_category(category_id, skip, limit)
            else:
                products = await self.repo.list_by_category(category_id, skip, limit)
        else:
            products = await self.repo.list_with_category(skip, limit)
        # All products here have .category loaded
        return [ProductDetailOut.model_validate(p, from_attributes=True) for p in products]

    async def create(self, payload: ProductCreate) -> Product:
        """Admin: create a new product."""
        # price is the selling price, mrp is the maximum retail price (optional)
        product = Product(**payload.model_dump())
        return await self.repo.create(product)

    async def update(self, product_id: UUID, payload: ProductUpdate) -> Product:
        """Admin: partially update a product. Auto-flags out-of-stock."""
        product = await self.repo.get_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
            )
        data = payload.model_dump(exclude_none=True)
        if not data:
            return product

        # Validate MRP vs Price for partial updates
        new_price = data.get("price", product.price)
        new_mrp = data.get("mrp", product.mrp)
        
        if new_mrp is not None and new_mrp < new_price:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"MRP (₹{new_mrp}) cannot be less than selling price (₹{new_price})"
            )

        if "stock" in data:
            new_stock = data["stock"]
            was_in_stock = not product.is_out_of_stock
            data["is_out_of_stock"] = new_stock <= 0
            if was_in_stock and new_stock <= 0:
                await self._notify_out_of_stock(product)

        # price is the selling price, mrp is the maximum retail price (optional)
        return await self.repo.update(product, data)

    async def adjust_stock(self, product_id: UUID, payload: StockAdjust) -> Product:
        """Admin: set stock to the given absolute value and flag out-of-stock."""
        product = await self.repo.get_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
            )
        was_in_stock = not product.is_out_of_stock
        new_stock = payload.stock
        data = {"stock": new_stock, "is_out_of_stock": new_stock <= 0}
        updated = await self.repo.update(product, data)
        if was_in_stock and new_stock <= 0:
            await self._notify_out_of_stock(updated)
        return updated

    async def _notify_out_of_stock(self, product: Product) -> None:
        """Save in-app notifications for all active users and send FCM broadcast."""
        users = await self.user_repo.list_active(0, 10_000)
        for user in users:
            notif = Notification(
                user_id=user.id,
                title="Out of Stock",
                body=f'"{product.name}" is now out of stock.',
            )
            self.notif_repo.db.add(notif)

        # FCM push to all registered devices
        all_tokens = await self.device_repo.get_all_tokens()
        await send_push(
            all_tokens,
            "Product Out of Stock ⚠️",
            f'"{product.name}" is currently out of stock.',
        )
