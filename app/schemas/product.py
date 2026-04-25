from __future__ import annotations

from uuid import UUID

from pydantic import Field, field_validator, model_validator

from app.core.config import settings
from app.models.product import CategoryType
from app.schemas.base import BaseSchema, TimestampSchema


# ── Helper function ───────────────────────────────────────────────────────────

def make_full_url(image_url: str | None) -> str | None:
    """Convert relative path to full URL if needed."""
    if not image_url:
        return None
    # If already a full URL, return as-is
    if image_url.startswith('http://') or image_url.startswith('https://'):
        return image_url
    # Convert relative path to full URL
    normalized = image_url.replace('\\', '/')
    if normalized.startswith('/'):
        normalized = normalized[1:]
    return f"{settings.SERVER_URL}/{normalized}"


def _empty_to_none(v: str | None) -> str | None:
    """Convert empty/whitespace-only strings to None."""
    if isinstance(v, str) and not v.strip():
        return None
    return v


# ─────────────────────────────────────────────────────────────────────────────
# Category
# ─────────────────────────────────────────────────────────────────────────────

class CategoryCreate(BaseSchema):
    """Admin: create a new product category."""

    name: str = Field(..., min_length=2, max_length=100)
    name_hi: str | None = Field(default=None, max_length=100)
    slug: str | None = Field(default=None, min_length=2, max_length=120, pattern=r"^[a-z0-9-]+$")
    # type is optional — parent categories may have no type; assign types to sub-categories
    type: CategoryType | None = None
    description: str | None = None
    description_hi: str | None = None
    image_url: str | None = None
    parent_id: UUID | None = None
    sort_order: int = Field(default=0, ge=0)
    show_in_nav: bool = False
    show_on_top: bool = False

    _normalize_hi = field_validator('name_hi', 'description_hi', mode='before')(lambda v: _empty_to_none(v))


class CategoryUpdate(BaseSchema):
    """Admin: partial update of a category (all fields optional)."""

    name: str | None = Field(default=None, min_length=2, max_length=100)
    name_hi: str | None = Field(default=None, max_length=100)
    description: str | None = None
    description_hi: str | None = None
    image_url: str | None = None
    is_active: bool | None = None
    type: CategoryType | None = None
    parent_id: UUID | None = None
    sort_order: int | None = None
    show_in_nav: bool | None = None
    show_on_top: bool | None = None


class CategoryOut(TimestampSchema):
    """Category response (flat, no nested children)."""

    name: str
    name_hi: str | None
    slug: str
    type: CategoryType | None
    description: str | None
    description_hi: str | None
    image_url: str | None
    is_active: bool
    sort_order: int
    show_in_nav: bool
    show_on_top: bool
    parent_id: UUID | None
    
    @field_validator('image_url', mode='before')
    @classmethod
    def convert_image_url(cls, v):
        """Convert relative path to full URL."""
        return make_full_url(v)


class CategoryWithChildrenOut(CategoryOut):
    """Category response including immediate subcategories."""

    children: list[CategoryOut] = []


# ─────────────────────────────────────────────────────────────────────────────
# Product
# ─────────────────────────────────────────────────────────────────────────────

class ProductCreate(BaseSchema):
    """Admin: create a new product."""

    name: str = Field(..., min_length=2, max_length=200)
    name_hi: str | None = Field(default=None, max_length=200)
    description: str | None = None
    description_hi: str | None = None
    price: float = Field(..., gt=0)
    mrp: float | None = Field(default=None, gt=0)
    stock: int = Field(default=0, ge=0)
    unit: str = Field(default="piece", max_length=50)  # kg | piece | litre …
    image_url: str | None = None
    category_id: UUID

    _normalize_hi = field_validator('name_hi', 'description_hi', mode='before')(lambda v: _empty_to_none(v))

    @model_validator(mode='after')
    def validate_mrp(self) -> 'ProductCreate':
        """Ensure MRP is not less than price."""
        if self.mrp is not None and self.mrp < self.price:
            raise ValueError(f"MRP (₹{self.mrp}) cannot be less than selling price (₹{self.price})")
        return self


class ProductUpdate(BaseSchema):
    """Admin: partial update of a product (all fields optional)."""

    name: str | None = Field(default=None, min_length=2, max_length=200)
    name_hi: str | None = Field(default=None, max_length=200)
    description: str | None = None
    description_hi: str | None = None
    price: float | None = Field(default=None, gt=0)
    mrp: float | None = Field(default=None, gt=0)
    stock: int | None = Field(default=None, ge=0)
    unit: str | None = None
    image_url: str | None = None
    category_id: UUID | None = None
    is_active: bool | None = None
    hsn_code: str | None = Field(default=None, max_length=20)
    gst_rate: float | None = Field(default=None, ge=0, le=100)

    @model_validator(mode='after')
    def validate_mrp(self) -> 'ProductUpdate':
        """Ensure MRP is not less than price when both are provided."""
        if self.price is not None and self.mrp is not None and self.mrp < self.price:
            raise ValueError(f"MRP (₹{self.mrp}) cannot be less than selling price (₹{self.price})")
        return self


class StockAdjust(BaseSchema):
    """Admin: adjust stock quantity directly."""

    stock: int = Field(..., ge=0, description="New absolute stock value")


class ProductOut(TimestampSchema):
    """Product response — flat (category_id only)."""

    name: str
    name_hi: str | None
    description: str | None
    description_hi: str | None
    price: float
    mrp: float | None
    stock: int
    unit: str
    image_url: str | None
    is_active: bool
    is_out_of_stock: bool
    hsn_code: str | None = None
    gst_rate: float | None = None
    category_id: UUID
    
    @field_validator('image_url', mode='before')
    @classmethod
    def convert_image_url(cls, v):
        """Convert relative path to full URL."""
        return make_full_url(v)


class ProductDetailOut(ProductOut):
    """Product response with full nested category object."""

    category: CategoryOut

