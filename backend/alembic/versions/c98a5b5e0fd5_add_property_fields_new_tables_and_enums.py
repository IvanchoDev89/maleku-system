"""add property fields, new tables and enums

Revision ID: c98a5b5e0fd5
Revises: 001_initial
Create Date: 2026-04-21 14:59:54.416636

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c98a5b5e0fd5"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types first
    property_category = sa.Enum(
        "BEACH", "MOUNTAIN", "JUNGLE", "CITY", "RURAL", "LAKE", name="propertycategory"
    )
    property_category.create(op.get_bind(), checkfirst=True)

    # Properties columns
    op.add_column(
        "properties",
        sa.Column("short_description", sa.String(length=500), nullable=True),
    )
    op.add_column("properties", sa.Column("category", property_category, nullable=True))
    op.add_column(
        "properties", sa.Column("district", sa.String(length=100), nullable=True)
    )
    op.add_column(
        "properties", sa.Column("map_address", sa.String(length=500), nullable=True)
    )
    op.add_column(
        "properties", sa.Column("cover_image", sa.String(length=500), nullable=True)
    )
    op.add_column("properties", sa.Column("videos", sa.JSON(), nullable=True))
    op.add_column(
        "properties",
        sa.Column("virtual_tour_url", sa.String(length=500), nullable=True),
    )
    op.add_column("properties", sa.Column("features", sa.JSON(), nullable=True))
    op.add_column("properties", sa.Column("house_rules", sa.Text(), nullable=True))
    op.add_column("properties", sa.Column("important_info", sa.Text(), nullable=True))
    op.add_column("properties", sa.Column("beds", sa.Integer(), nullable=True))
    op.add_column("properties", sa.Column("baths", sa.Integer(), nullable=True))
    op.add_column("properties", sa.Column("square_meters", sa.Integer(), nullable=True))
    op.add_column("properties", sa.Column("base_price", sa.Float(), nullable=True))
    op.add_column(
        "properties", sa.Column("currency", sa.String(length=3), nullable=True)
    )
    op.add_column("properties", sa.Column("weekend_price", sa.Float(), nullable=True))
    op.add_column("properties", sa.Column("weekly_discount", sa.Float(), nullable=True))
    op.add_column(
        "properties", sa.Column("seo_title", sa.String(length=255), nullable=True)
    )
    op.add_column("properties", sa.Column("seo_description", sa.Text(), nullable=True))
    op.add_column("properties", sa.Column("seo_keywords", sa.JSON(), nullable=True))
    op.add_column(
        "properties", sa.Column("seo_slug", sa.String(length=255), nullable=True)
    )
    op.add_column("properties", sa.Column("is_verified", sa.Boolean(), nullable=True))
    op.create_index("idx_property_category", "properties", ["category"], unique=False)

    # Rooms columns
    op.add_column(
        "rooms",
        sa.Column("slug", sa.String(length=255), nullable=False, server_default=""),
    )
    op.add_column("rooms", sa.Column("room_type", sa.String(length=50), nullable=True))
    op.add_column("rooms", sa.Column("bath_count", sa.Float(), nullable=True))
    op.add_column("rooms", sa.Column("square_meters", sa.Integer(), nullable=True))
    op.add_column("rooms", sa.Column("base_price", sa.Float(), nullable=True))
    op.add_column("rooms", sa.Column("weekend_price", sa.Float(), nullable=True))
    op.add_column("rooms", sa.Column("is_featured", sa.Boolean(), nullable=True))


def downgrade() -> None:
    op.drop_column("rooms", "is_featured")
    op.drop_column("rooms", "weekend_price")
    op.drop_column("rooms", "base_price")
    op.drop_column("rooms", "square_meters")
    op.drop_column("rooms", "bath_count")
    op.drop_column("rooms", "room_type")
    op.drop_column("rooms", "slug")
    op.drop_index("idx_property_category", table_name="properties")
    op.drop_column("properties", "is_verified")
    op.drop_column("properties", "seo_slug")
    op.drop_column("properties", "seo_keywords")
    op.drop_column("properties", "seo_description")
    op.drop_column("properties", "seo_title")
    op.drop_column("properties", "weekly_discount")
    op.drop_column("properties", "weekend_price")
    op.drop_column("properties", "currency")
    op.drop_column("properties", "base_price")
    op.drop_column("properties", "square_meters")
    op.drop_column("properties", "baths")
    op.drop_column("properties", "beds")
    op.drop_column("properties", "important_info")
    op.drop_column("properties", "house_rules")
    op.drop_column("properties", "features")
    op.drop_column("properties", "virtual_tour_url")
    op.drop_column("properties", "videos")
    op.drop_column("properties", "cover_image")
    op.drop_column("properties", "map_address")
    op.drop_column("properties", "district")
    op.drop_column("properties", "category")
    op.drop_column("properties", "short_description")

    # Drop enum
    sa.Enum(name="propertycategory").drop(op.get_bind(), checkfirst=True)
