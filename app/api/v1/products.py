from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.schemas.product import (
    CategoryCreate,
    CategoryOut,
    CategoryUpdate,
    CategoryWithChildrenOut,
    ProductCreate,
    ProductDetailOut,
    ProductOut,
    ProductUpdate,
    StockAdjust,
)
from app.services.product_service import CategoryService, ProductService

router = APIRouter(tags=["Products & Categories"])


# ── Categories ────────────────────────────────────────────────────────────────

@router.get("/categories/nav", response_model=list[CategoryOut])
async def list_nav_categories(db: Annotated[AsyncSession, Depends(get_db)]):
    """Return categories marked for bottom navigation (show_in_nav=True), active only."""
    return await CategoryService(db).list_nav()


@router.get("/categories/tree", response_model=list[CategoryWithChildrenOut])
async def list_categories_tree(db: Annotated[AsyncSession, Depends(get_db)]):
    """Return top-level categories with their subcategories nested."""
    return await CategoryService(db).list_with_children()


@router.get("/categories", response_model=list[CategoryOut])
async def list_categories(
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    parent_id: UUID | None = Query(default=None, description="Filter subcategories of a parent"),
    top_level: bool = Query(default=False, description="Return only top-level categories"),
):
    """Return active categories. Supports parent filter and top-level flag."""
    svc = CategoryService(db)
    if parent_id:
        return await svc.list_children(parent_id)
    if top_level:
        return await svc.list_top_level(skip, limit)
    return await svc.list_active(skip, limit)


@router.get("/categories/{category_id}", response_model=CategoryOut)
async def get_category(
    category_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Return a single category by ID."""
    return await CategoryService(db).get_category(category_id)


@router.post("/categories", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
async def create_category(
    payload: CategoryCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[object, Depends(get_current_admin)],
):
    """Admin: create a new category."""
    return await CategoryService(db).create(payload)


@router.patch("/categories/{category_id}", response_model=CategoryOut)
async def update_category(
    category_id: UUID,
    payload: CategoryUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[object, Depends(get_current_admin)],
):
    """Admin: partially update a category."""
    return await CategoryService(db).update(category_id, payload)


@router.get("/categories/{category_id}/details")
async def get_category_details(
    category_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Return subcategories if present, else products for a category.
    """
    from app.services.product_service import CategoryService, ProductService

    category = await CategoryService(db).get_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    subcategories = await CategoryService(db).list_children(category_id)
    if subcategories:
        return {"type": "subcategories", "data": subcategories}

    products = await ProductService(db).list_products_with_category(category_id, None, 0, 100, None)
    return {"type": "products", "data": products}

# ── Products ──────────────────────────────────────────────────────────────────

@router.get("/products", response_model=list[ProductDetailOut])
async def list_products(
    db: Annotated[AsyncSession, Depends(get_db)],
    category_id: UUID | None = Query(default=None),
    search: str | None = Query(default=None, min_length=1),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=30, ge=1, le=100),
    sort_by: str | None = Query(default=None, description="Sort by: 'popular' for most ordered"),
):
    """Return active products with nested category. Supports category filter, text search, and popularity sorting."""
    return await ProductService(db).list_products_with_category(category_id, search, skip, limit, sort_by)


@router.get("/products/{product_id}", response_model=ProductOut)
async def get_product(
    product_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Return a product by ID."""
    return await ProductService(db).get_product(product_id)


@router.get("/products/{product_id}/detail", response_model=ProductDetailOut)
async def get_product_detail(
    product_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Return a product with its full nested category object."""
    return await ProductService(db).get_detail(product_id)


@router.post("/products", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
async def create_product(
    payload: ProductCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[object, Depends(get_current_admin)],
):
    """Admin: create a new product."""
    return await ProductService(db).create(payload)


@router.patch("/products/{product_id}", response_model=ProductOut)
async def update_product(
    product_id: UUID,
    payload: ProductUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[object, Depends(get_current_admin)],
):
    """Admin: partially update a product."""
    return await ProductService(db).update(product_id, payload)


@router.post("/products/{product_id}/adjust-stock", response_model=ProductOut)
async def adjust_stock(
    product_id: UUID,
    payload: StockAdjust,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[object, Depends(get_current_admin)],
):
    """Admin: set the absolute stock level for a product."""
    return await ProductService(db).adjust_stock(product_id, payload)
