from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.order import OrderItem
from app.models.product import Category, Product
from app.repositories.base_repository import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    """CRUD + lookup queries for the Category model."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Category, db)

    # ── Specific queries ──────────────────────────────────────────────────────

    async def get_by_slug(self, slug: str) -> Category | None:
        """Return a category by its URL slug (only non-deleted)."""
        result = await self.db.execute(
            select(Category).where(Category.slug == slug, Category.is_deleted == False)
        )
        return result.scalars().first()

    async def get_by_slug_including_deleted(self, slug: str) -> Category | None:
        """Return a category by its URL slug, including soft-deleted ones."""
        result = await self.db.execute(
            select(Category).where(Category.slug == slug)
        )
        return result.scalars().first()

    async def soft_delete(self, category: Category) -> Category:
        """Soft delete a category by setting is_deleted=True."""
        return await self.update(category, {"is_deleted": True, "is_active": False})

    async def list_active(self, skip: int = 0, limit: int = 100):
        """Return all active, non-deleted categories (all levels), ordered by sort_order then name."""
        result = await self.db.execute(
            select(Category)
            .where(Category.is_active == True, Category.is_deleted == False)  
            .order_by(Category.sort_order, Category.name)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def list_all_including_deleted(self, skip: int = 0, limit: int = 100):
        """Return all categories including deleted ones (admin use), ordered by sort_order then name."""
        result = await self.db.execute(
            select(Category)
            .order_by(Category.is_deleted, Category.sort_order, Category.name)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def list_top_level_active(self, skip: int = 0, limit: int = 100):
        """Return active, non-deleted top-level categories (no parent), ordered by sort_order then name."""
        result = await self.db.execute(
            select(Category)
            .where(Category.is_active == True, Category.is_deleted == False, Category.parent_id == None)  
            .order_by(Category.sort_order, Category.name)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def list_nav(self):
        """Return active, non-deleted categories flagged for bottom navigation, ordered by sort_order."""
        result = await self.db.execute(
            select(Category)
            .where(Category.is_active == True, Category.is_deleted == False, Category.show_in_nav == True)  
            .order_by(Category.sort_order, Category.name)
        )
        return result.scalars().all()

    async def list_with_children(self, skip: int = 0, limit: int = 200):
        """Return all categories with their children eagerly loaded (admin use)."""
        result = await self.db.execute(
            select(Category)
            .options(selectinload(Category.children))
            .where(Category.parent_id == None, Category.is_deleted == False)
            .order_by(Category.sort_order, Category.name)
            .offset(skip)
            .limit(limit)
        )
        categories = result.scalars().all()
        
        # Filter out deleted children
        for category in categories:
            category.children = [child for child in category.children if not child.is_deleted]
        
        return categories

    async def list_children(self, parent_id: UUID):
        """Return all active, non-deleted subcategories of a given parent."""
        result = await self.db.execute(
            select(Category)
            .where(Category.parent_id == parent_id, Category.is_active == True, Category.is_deleted == False)  
            .order_by(Category.sort_order, Category.name)
        )
        return result.scalars().all()


class ProductRepository(BaseRepository[Product]):
    """CRUD + lookup queries for the Product model."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Product, db)

    # ── Specific queries ──────────────────────────────────────────────────────

    async def get_with_category(self, product_id: UUID) -> Product | None:
        """Return a product with its category eagerly loaded."""
        result = await self.db.execute(
            select(Product)
            .options(selectinload(Product.category))
            .where(Product.id == product_id)
        )
        return result.scalars().first()

    async def list_with_category(self, skip: int = 0, limit: int = 100):
        """Return all products with category eagerly loaded (for admin)."""
        result = await self.db.execute(
            select(Product)
            .where(Product.is_deleted == False)  
            .options(selectinload(Product.category))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def list_active(self, skip: int = 0, limit: int = 50):
        """Return all active, non-deleted products."""
        result = await self.db.execute(
            select(Product)
            .where(Product.is_active == True, Product.is_deleted == False)  
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def list_by_category(
        self, category_id: UUID, skip: int = 0, limit: int = 50
    ):
        """Return active, non-deleted products belonging to a specific category, with category eagerly loaded."""
        result = await self.db.execute(
            select(Product)
            .options(selectinload(Product.category))
            .where(
                Product.category_id == category_id,
                Product.is_active == True,  
                Product.is_deleted == False,  
            )
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def list_popular_by_category(
        self, category_id: UUID, skip: int = 0, limit: int = 50
    ):
        """Return active, non-deleted products by category, ordered by order count (most popular first), with category eagerly loaded."""
        # Subquery to count orders per product
        order_count_subquery = (
            select(
                OrderItem.product_id,
                func.count(OrderItem.id).label('order_count')
            )
            .group_by(OrderItem.product_id)
            .subquery()
        )
        # Main query: join products with order counts and sort by popularity
        result = await self.db.execute(
            select(Product)
            .options(selectinload(Product.category))
            .outerjoin(order_count_subquery, Product.id == order_count_subquery.c.product_id)
            .where(
                Product.category_id == category_id,
                Product.is_active == True,  
                Product.is_deleted == False,  
            )
            .order_by(
                func.coalesce(order_count_subquery.c.order_count, 0).desc(),
                Product.name
            )
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def list_out_of_stock(self):
        """Return all products currently flagged as out of stock."""
        result = await self.db.execute(
            select(Product).where(Product.is_out_of_stock == True)  
        )
        return result.scalars().all()

    async def search(self, query: str, skip: int = 0, limit: int = 50):
        """Case-insensitive substring search on product name, only for active and non-deleted products."""
        result = await self.db.execute(
            select(Product)
            .where(
                Product.name.ilike(f"%{query}%"),
                Product.is_active == True,  
                Product.is_deleted == False,  
            )
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def soft_delete(self, product: Product) -> Product:
        """Soft delete a product by setting is_deleted=True."""
        return await self.update(product, {"is_deleted": True, "is_active": False})
