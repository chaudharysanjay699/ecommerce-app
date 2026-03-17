from __future__ import annotations

import uuid

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin
from app.models.order import OrderStatus


class OrderTracking(Base, UUIDMixin, TimestampMixin):
    """Immutable audit log of every status transition for an order.

    A new row is inserted each time the order status changes, giving a full
    history of the order lifecycle (placed → confirmed → packed →
    out_for_delivery → delivered / cancelled).
    """

    __tablename__ = "order_tracking"

    order_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), index=True, nullable=False
    )

    # The status that was applied at this point in time
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, name="orderstatus", values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )

    # Optional human-readable context (e.g. "Package picked up by rider")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Actor who triggered the transition (admin user id or "system")
    changed_by: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="tracking")
