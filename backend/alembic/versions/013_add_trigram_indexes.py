"""add pg_trgm extension and trigram indexes for ILIKE search performance

Revision ID: 013
Revises: 012
Create Date: 2026-06-25 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "013"
down_revision: Union[str, None] = "012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    op.create_index(
        "idx_property_region_trgm",
        "properties",
        [sa.text("region gin_trgm_ops")],
        postgresql_using="gin",
    )
    op.create_index(
        "idx_tour_location_trgm",
        "tours",
        [sa.text("location gin_trgm_ops")],
        postgresql_using="gin",
    )
    op.create_index(
        "idx_property_city_trgm",
        "properties",
        [sa.text("city gin_trgm_ops")],
        postgresql_using="gin",
    )
    op.create_index(
        "idx_destination_name_trgm",
        "destinations",
        [sa.text("name gin_trgm_ops")],
        postgresql_using="gin",
    )
    op.create_index(
        "idx_destination_region_trgm",
        "destinations",
        [sa.text("region gin_trgm_ops")],
        postgresql_using="gin",
    )


def downgrade() -> None:
    op.drop_index("idx_property_region_trgm", table_name="properties")
    op.drop_index("idx_tour_location_trgm", table_name="tours")
    op.drop_index("idx_property_city_trgm", table_name="properties")
    op.drop_index("idx_destination_name_trgm", table_name="destinations")
    op.drop_index("idx_destination_region_trgm", table_name="destinations")
