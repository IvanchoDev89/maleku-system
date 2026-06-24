"""migrate tour category 'culture' -> 'cultural'

Revision ID: 012
Revises: 011
Create Date: 2026-06-23

"""

from typing import Union, Sequence
from alembic import op

revision: str = "012"
down_revision: Union[str, None] = "011"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_context().bind
    if bind.dialect.name == "postgresql":
        op.execute("UPDATE tours SET category = 'cultural' WHERE category = 'culture'")


def downgrade() -> None:
    pass
