"""normalize tour difficulty values: moderate->medium, challenging->hard

Revision ID: 011
Revises: 10208a737f40
Create Date: 2026-06-23

"""

from typing import Union, Sequence
from alembic import op

revision: str = "011"
down_revision: Union[str, None] = "10208a737f40"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_context().bind
    if bind.dialect.name == "postgresql":
        op.execute(
            "UPDATE tours SET difficulty = 'medium' WHERE difficulty = 'moderate'"
        )
        op.execute(
            "UPDATE tours SET difficulty = 'hard' WHERE difficulty = 'challenging'"
        )


def downgrade() -> None:
    pass
