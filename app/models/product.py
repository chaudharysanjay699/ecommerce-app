from __future__ import annotations

import enum
import uuid

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class CategoryType(str, enum.Enum):
    GROCERY = "grocery"
    VEGETABLE = "vegetable"
    BASKET = "basket"
    COPY_PEN = "copy_pen"


class Category(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    # type is now optional — parent categories may not need a type; sub-categories inherit context
    type: Mapped[CategoryType | None] = mapped_column(
        Enum(CategoryType, values_callable=lambda e: [x.value for x in e]),
        nullable=True,
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    # show_in_nav=True makes this category appear in the bottom navigation bar
    show_in_nav: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # show_on_top=True pins this category to the top of the homepage / categories listing
    show_on_top: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Self-referential: parent_id=None means top-level / parent category
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True
    )

    parent: Mapped["Category | None"] = relationship(
        "Category", remote_side="Category.id", back_populates="children"
    )
    children: Mapped[list["Category"]] = relationship(
        "Category", back_populates="parent", cascade="all, delete-orphan"
    )
    products: Mapped[list["Product"]] = relationship("Product", back_populates="category")



class Product(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "products"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    mrp: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    unit: Mapped[str] = mapped_column(String(50), default="piece")  # kg, piece, litre …
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    is_out_of_stock: Mapped[bool] = mapped_column(Boolean, default=False)

    category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("categories.id", ondelete="RESTRICT"), index=True)

    category: Mapped["Category"] = relationship("Category", back_populates="products")
    cart_items: Mapped[list["CartItem"]] = relationship("CartItem", back_populates="product")
    order_items: Mapped[list["OrderItem"]] = relationship("OrderItem", back_populates="product")
    offer: Mapped["Offer | None"] = relationship("Offer", back_populates="product", uselist=False)
    wishlist_items: Mapped[list["WishlistItem"]] = relationship("WishlistItem", back_populates="product", cascade="all, delete-orphan")
