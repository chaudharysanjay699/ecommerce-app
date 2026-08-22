"""Merge holiday delivery and soft-delete migration branches."""

from typing import Sequence, Union


revision: str = "0015_merge_holiday_soft_delete"
down_revision: Union[str, Sequence[str], None] = (
    "0011_add_holiday_delivery_dates",
    "0014",
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
