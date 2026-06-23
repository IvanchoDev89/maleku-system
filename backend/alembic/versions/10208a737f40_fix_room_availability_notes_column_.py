"""fix room_availability notes column Float->Text

Migration 004 created ``room_availability.notes`` as ``sa.Float()``,
but the model defines it as ``Text``.  Migration 006 only fixes the
issue on databases where the table was *not* created by 004 (it wraps
``create_table`` with a ``_table_exists`` guard), so DBs that ran the
full 004→005→5c57a60106d5→006 chain still have ``notes::double precision``.

Revision ID: 10208a737f40
Revises: 008
Create Date: 2026-06-22 23:38:19.965331

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "10208a737f40"
down_revision: Union[str, None] = "008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    row = bind.execute(
        sa.text(
            "SELECT data_type FROM information_schema.columns "
            "WHERE table_name = 'room_availability' AND column_name = 'notes'"
        )
    ).scalar()
    if row and row.lower() in ("double precision", "real", "float"):
        op.alter_column(
            "room_availability",
            "notes",
            type_=sa.Text(),
            postgresql_using="notes::text",
        )


def downgrade() -> None:
    pass
