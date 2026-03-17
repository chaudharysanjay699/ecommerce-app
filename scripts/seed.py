"""Seed script – inserts sample categories and products.

Usage (from the project root):
    python -m scripts.seed
    # or
    python scripts/seed.py

Idempotent: categories and products are matched by slug / name so re-running
won't create duplicates.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Make sure the project root is on the path when run directly
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal, engine
from app.models.product import Category, CategoryType, Product


# ── Seed data ─────────────────────────────────────────────────────────────────

CATEGORIES: list[dict] = [
    {
        "slug": "fresh-vegetables",
        "name": "Fresh Vegetables",
        "type": CategoryType.VEGETABLE,
        "description": "Farm-fresh vegetables delivered daily (order window: 5-9 AM).",
    },
    {
        "slug": "grocery-staples",
        "name": "Grocery Staples",
        "type": CategoryType.GROCERY,
        "description": "Everyday pantry essentials.",
    },
    {
        "slug": "fruit-baskets",
        "name": "Fruit Baskets",
        "type": CategoryType.BASKET,
        "description": "Curated seasonal fruit baskets.",
    },
    {
        "slug": "stationery",
        "name": "Stationery & School Supplies",
        "type": CategoryType.COPY_PEN,
        "description": "Notebooks, pens, and office supplies.",
    },
]

# Each product entry has a "category_slug" key used to resolve the FK.
PRODUCTS: list[dict] = [
    # ── Vegetables ────────────────────────────────────────────────────────────
    {
        "category_slug": "fresh-vegetables",
        "name": "Tomatoes",
        "description": "Ripe red tomatoes, perfect for salads and curries.",
        "price": 25.00,
        "stock": 100,
        "unit": "kg",
    },
    {
        "category_slug": "fresh-vegetables",
        "name": "Spinach",
        "description": "Tender baby spinach leaves.",
        "price": 15.00,
        "stock": 80,
        "unit": "bunch",
    },
    {
        "category_slug": "fresh-vegetables",
        "name": "Onions",
        "description": "Premium red onions.",
        "price": 20.00,
        "stock": 150,
        "unit": "kg",
    },
    {
        "category_slug": "fresh-vegetables",
        "name": "Potatoes",
        "description": "Fresh farm potatoes.",
        "price": 18.00,
        "stock": 200,
        "unit": "kg",
    },
    {
        "category_slug": "fresh-vegetables",
        "name": "Carrots",
        "description": "Crunchy orange carrots.",
        "price": 30.00,
        "stock": 90,
        "unit": "kg",
    },
    # ── Grocery ───────────────────────────────────────────────────────────────
    {
        "category_slug": "grocery-staples",
        "name": "Basmati Rice (5 kg)",
        "description": "Long-grain aged basmati rice.",
        "price": 380.00,
        "stock": 60,
        "unit": "bag",
    },
    {
        "category_slug": "grocery-staples",
        "name": "Whole Wheat Flour (10 kg)",
        "description": "Stone-ground whole wheat atta.",
        "price": 290.00,
        "stock": 50,
        "unit": "bag",
    },
    {
        "category_slug": "grocery-staples",
        "name": "Sunflower Oil (1 L)",
        "description": "Refined sunflower cooking oil.",
        "price": 120.00,
        "stock": 75,
        "unit": "bottle",
    },
    {
        "category_slug": "grocery-staples",
        "name": "Toor Dal (1 kg)",
        "description": "Split pigeon peas.",
        "price": 95.00,
        "stock": 120,
        "unit": "pack",
    },
    {
        "category_slug": "grocery-staples",
        "name": "Full Cream Milk (1 L)",
        "description": "Fresh pasteurised full-cream milk.",
        "price": 58.00,
        "stock": 200,
        "unit": "litre",
    },
    # ── Fruit Baskets ─────────────────────────────────────────────────────────
    {
        "category_slug": "fruit-baskets",
        "name": "Mixed Fruit Basket (Small)",
        "description": "Seasonal mix: apples, bananas, oranges (approx. 2 kg).",
        "price": 199.00,
        "stock": 30,
        "unit": "basket",
    },
    {
        "category_slug": "fruit-baskets",
        "name": "Premium Mango Box",
        "description": "Alphonso mangoes – 12 pieces.",
        "price": 450.00,
        "stock": 20,
        "unit": "box",
    },
    {
        "category_slug": "fruit-baskets",
        "name": "Berry Delight Basket",
        "description": "Strawberries, blueberries, and grapes.",
        "price": 320.00,
        "stock": 15,
        "unit": "basket",
    },
    # ── Stationery ────────────────────────────────────────────────────────────
    {
        "category_slug": "stationery",
        "name": "A4 Notebook (200 pages)",
        "description": "Single-ruled A4 notebook.",
        "price": 45.00,
        "stock": 500,
        "unit": "piece",
    },
    {
        "category_slug": "stationery",
        "name": "Ball-point Pen Set (10 pcs)",
        "description": "Blue and black ball-point pens.",
        "price": 60.00,
        "stock": 300,
        "unit": "set",
    },
    {
        "category_slug": "stationery",
        "name": "Geometry Box",
        "description": "Complete geometry set with compass, protractor, and scales.",
        "price": 85.00,
        "stock": 150,
        "unit": "piece",
    },
]


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _upsert_category(session: AsyncSession, data: dict) -> Category:
    result = await session.execute(
        select(Category).where(Category.slug == data["slug"])
    )
    category = result.scalar_one_or_none()
    if category is None:
        category = Category(
            name=data["name"],
            slug=data["slug"],
            type=data["type"],
            description=data.get("description"),
        )
        session.add(category)
        await session.flush()
        print(f"  [+] Category created: {category.name}")
    else:
        print(f"  [=] Category exists:  {category.name}")
    return category


async def _upsert_product(
    session: AsyncSession,
    data: dict,
    category: Category,
) -> Product:
    result = await session.execute(
        select(Product).where(
            Product.name == data["name"],
            Product.category_id == category.id,
        )
    )
    product = result.scalar_one_or_none()
    if product is None:
        product = Product(
            name=data["name"],
            description=data.get("description"),
            price=data["price"],
            stock=data["stock"],
            unit=data.get("unit", "piece"),
            category_id=category.id,
            is_out_of_stock=data["stock"] <= 0,
        )
        session.add(product)
        await session.flush()
        print(f"      [+] Product created: {product.name}")
    else:
        print(f"      [=] Product exists:  {product.name}")
    return product


# ── Main ──────────────────────────────────────────────────────────────────────

async def seed() -> None:
    print("\n=== Seeding database ===\n")

    async with AsyncSessionLocal() as session:
        # Build a slug → Category map
        category_map: dict[str, Category] = {}
        print("── Categories ──────────────────────────────────────────")
        for cat_data in CATEGORIES:
            cat = await _upsert_category(session, cat_data)
            category_map[cat_data["slug"]] = cat

        print("\n── Products ────────────────────────────────────────────")
        for prod_data in PRODUCTS:
            slug = prod_data.pop("category_slug")
            category = category_map[slug]
            await _upsert_product(session, prod_data, category)
            prod_data["category_slug"] = slug  # restore for idempotency

        await session.commit()

    await engine.dispose()
    print("\n=== Seed complete ===\n")


if __name__ == "__main__":
    asyncio.run(seed())
