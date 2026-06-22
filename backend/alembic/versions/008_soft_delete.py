"""add deleted_at column to destinations for soft delete

Revision ID: 008
Revises: 007
Create Date: 2026-06-19

"""

from typing import Union, Sequence
from alembic import op
import sqlalchemy as sa

revision: str = "008"
down_revision: Union[str, None] = "007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _column_exists(table: str, column: str) -> bool:
    bind = op.get_context().bind
    insp = sa.inspect(bind)
    columns = [c["name"] for c in insp.get_columns(table)]
    return column in columns


def upgrade() -> None:
    if not _column_exists("destinations", "deleted_at"):
        op.add_column(
            "destinations",
            sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        )


def downgrade() -> None:
    if _column_exists("destinations", "deleted_at"):
        op.drop_column("destinations", "deleted_at")
