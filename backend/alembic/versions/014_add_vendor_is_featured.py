"""add is_featured column to vendors table

Revision ID: 014
Revises: 95526b2e75d5
Create Date: 2026-06-30 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "014"
down_revision: Union[str, None] = "95526b2e75d5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "vendors",
        sa.Column("is_featured", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.create_index("idx_vendor_featured", "vendors", ["is_featured"])


def downgrade() -> None:
    op.drop_index("idx_vendor_featured", table_name="vendors")
    op.drop_column("vendors", "is_featured")
