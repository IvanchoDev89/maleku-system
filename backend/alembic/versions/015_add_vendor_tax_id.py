"""add tax_id column to vendors table

Revision ID: 015
Revises: 014
Create Date: 2026-06-30 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "015"
down_revision: Union[str, None] = "014"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "vendors",
        sa.Column("tax_id", sa.String(50), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("vendors", "tax_id")
