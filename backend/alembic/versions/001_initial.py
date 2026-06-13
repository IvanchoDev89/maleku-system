"""Initial migration with all tables

Revision ID: 001_initial
Revises:
Create Date: 2024-01-01

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users table
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("username", sa.String(length=100), nullable=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("avatar_url", sa.String(length=500), nullable=True),
        sa.Column(
            "role",
            sa.Enum("SUPER_ADMIN", "VENDOR", "CLIENT", name="userrole"),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_user_email", "users", ["email"], unique=True)
    op.create_index("idx_user_username", "users", ["username"], unique=True)

    # Vendors table
    op.create_table(
        "vendors",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("business_name", sa.String(length=255), nullable=False),
        sa.Column("business_slug", sa.String(length=255), nullable=False),
        sa.Column("business_type", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("logo_url", sa.String(length=500), nullable=True),
        sa.Column("cover_image", sa.String(length=500), nullable=True),
        sa.Column("address", sa.String(length=500), nullable=True),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("rating", sa.Float(), nullable=True),
        sa.Column("total_reviews", sa.Integer(), nullable=True),
        sa.Column("commission_rate", sa.Float(), nullable=True),
        sa.Column("stripe_account_id", sa.String(length=255), nullable=True),
        sa.Column("stripe_connected", sa.Boolean(), nullable=True),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_vendor_slug", "vendors", ["business_slug"], unique=True)
    op.create_index("idx_vendor_type", "vendors", ["business_type"])

    # Properties table
    op.create_table(
        "properties",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("vendor_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "property_type",
            sa.Enum(
                "HOTEL",
                "HOSTEL",
                "ECO_LODGE",
                "RESORT",
                "VILLA",
                "APARTMENT",
                "CABIN",
                "GLAMPING",
                name="propertytype",
            ),
            nullable=False,
        ),
        sa.Column("country", sa.String(length=100), nullable=False),
        sa.Column("province", sa.String(length=100), nullable=True),
        sa.Column("region", sa.String(length=100), nullable=True),
        sa.Column("city", sa.String(length=100), nullable=True),
        sa.Column("address", sa.String(length=500), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("amenities", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("images", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("check_in_time", sa.String(length=10), nullable=True),
        sa.Column("check_out_time", sa.String(length=10), nullable=True),
        sa.Column("cancellation_policy", sa.Text(), nullable=True),
        sa.Column("min_guests", sa.Integer(), nullable=True),
        sa.Column("max_guests", sa.Integer(), nullable=True),
        sa.Column("rating", sa.Float(), nullable=True),
        sa.Column("total_reviews", sa.Integer(), nullable=True),
        sa.Column("total_bookings", sa.Integer(), nullable=True),
        sa.Column("is_featured", sa.Boolean(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["vendor_id"], ["vendors.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_property_slug", "properties", ["slug"], unique=True)
    op.create_index("idx_property_vendor", "properties", ["vendor_id"])
    op.create_index("idx_property_region", "properties", ["region"])
    op.create_index("idx_property_type", "properties", ["property_type"])

    # Rooms table
    op.create_table(
        "rooms",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("property_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("max_occupancy", sa.Integer(), nullable=True),
        sa.Column("bed_type", sa.String(length=50), nullable=True),
        sa.Column("bed_count", sa.Integer(), nullable=True),
        sa.Column("amenities", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("images", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("price_per_night", sa.Float(), nullable=True),
        sa.Column("currency", sa.String(length=3), nullable=True),
        sa.Column("extra_guest_price", sa.Float(), nullable=True),
        sa.Column("is_available", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["property_id"], ["properties.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Tours table
    op.create_table(
        "tours",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("vendor_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "category",
            sa.Enum(
                "ADVENTURE",
                "NATURE",
                "CULTURAL",
                "WATER",
                "WELLNESS",
                "GASTRONOMY",
                name="tourcategory",
            ),
            nullable=False,
        ),
        sa.Column(
            "difficulty",
            sa.Enum("EASY", "MODERATE", "CHALLENGING", name="tourdifficulty"),
            nullable=True,
        ),
        sa.Column("duration_hours", sa.Float(), nullable=False),
        sa.Column("duration_text", sa.String(length=50), nullable=True),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("meeting_point", sa.String(length=500), nullable=True),
        sa.Column("included", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "not_included", postgresql.JSON(astext_type=sa.Text()), nullable=True
        ),
        sa.Column("itinerary", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("max_group_size", sa.Integer(), nullable=True),
        sa.Column("min_age", sa.Integer(), nullable=True),
        sa.Column("price", sa.Float(), nullable=True),
        sa.Column("currency", sa.String(length=3), nullable=True),
        sa.Column("images", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("cover_image", sa.String(length=500), nullable=True),
        sa.Column(
            "schedule_days", postgresql.JSON(astext_type=sa.Text()), nullable=True
        ),
        sa.Column("rating", sa.Float(), nullable=True),
        sa.Column("total_reviews", sa.Integer(), nullable=True),
        sa.Column("total_bookings", sa.Integer(), nullable=True),
        sa.Column("is_featured", sa.Boolean(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["vendor_id"], ["vendors.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_tour_slug", "tours", ["slug"], unique=True)
    op.create_index("idx_tour_vendor", "tours", ["vendor_id"])
    op.create_index("idx_tour_category", "tours", ["category"])

    # Bookings table
    op.create_table(
        "bookings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("vendor_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("property_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("room_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("tour_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("booking_type", sa.String(length=20), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "PENDING",
                "CONFIRMED",
                "CANCELLED",
                "COMPLETED",
                "REFUNDED",
                name="bookingstatus",
            ),
            nullable=False,
        ),
        sa.Column("check_in", sa.DateTime(), nullable=True),
        sa.Column("check_out", sa.DateTime(), nullable=True),
        sa.Column("guests", sa.Integer(), nullable=True),
        sa.Column("participants", sa.Integer(), nullable=True),
        sa.Column("guest_name", sa.String(length=255), nullable=False),
        sa.Column("guest_email", sa.String(length=255), nullable=False),
        sa.Column("guest_phone", sa.String(length=20), nullable=True),
        sa.Column("guest_notes", sa.Text(), nullable=True),
        sa.Column("subtotal", sa.Float(), nullable=True),
        sa.Column("commission_amount", sa.Float(), nullable=True),
        sa.Column("total_amount", sa.Float(), nullable=True),
        sa.Column("currency", sa.String(length=3), nullable=True),
        sa.Column("stripe_payment_intent_id", sa.String(length=255), nullable=True),
        sa.Column("stripe_payment_status", sa.String(length=50), nullable=True),
        sa.Column("confirmation_code", sa.String(length=20), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["vendor_id"], ["vendors.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(
            ["property_id"], ["properties.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(["room_id"], ["rooms.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["tour_id"], ["tours.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_booking_user", "bookings", ["user_id"])
    op.create_index("idx_booking_vendor", "bookings", ["vendor_id"])
    op.create_index("idx_booking_property", "bookings", ["property_id"])
    op.create_index("idx_booking_status", "bookings", ["status"])
    op.create_index(
        "idx_booking_confirmation", "bookings", ["confirmation_code"], unique=True
    )

    # Blog posts table
    op.create_table(
        "blog_posts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("excerpt", sa.Text(), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("featured_image", sa.String(length=500), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("tags", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("author_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "status",
            sa.Enum("DRAFT", "PUBLISHED", "ARCHIVED", name="blogpoststatus"),
            nullable=False,
        ),
        sa.Column("published_at", sa.DateTime(), nullable=True),
        sa.Column("views_count", sa.Integer(), nullable=True),
        sa.Column("is_featured", sa.Boolean(), nullable=True),
        sa.Column("seo_title", sa.String(length=255), nullable=True),
        sa.Column("seo_description", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_blog_slug", "blog_posts", ["slug"], unique=True)
    op.create_index("idx_blog_status", "blog_posts", ["status"])

    # Destinations table
    op.create_table(
        "destinations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("region", sa.String(length=100), nullable=True),
        sa.Column("province", sa.String(length=100), nullable=True),
        sa.Column("highlights", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "things_to_do", postgresql.JSON(astext_type=sa.Text()), nullable=True
        ),
        sa.Column("best_time", sa.Text(), nullable=True),
        sa.Column("image", sa.String(length=500), nullable=True),
        sa.Column("gallery", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("order", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_featured", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_destination_slug", "destinations", ["slug"], unique=True)
    op.create_index("idx_destination_region", "destinations", ["region"])

    # Reviews table
    op.create_table(
        "reviews",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("property_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("tour_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("is_approved", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["property_id"], ["properties.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tour_id"], ["tours.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_review_property", "reviews", ["property_id"])
    op.create_index("idx_review_tour", "reviews", ["tour_id"])
    op.create_index("idx_review_user", "reviews", ["user_id"])


def downgrade() -> None:
    op.drop_table("reviews")
    op.drop_table("destinations")
    op.drop_table("blog_posts")
    op.drop_table("bookings")
    op.drop_table("tours")
    op.drop_table("rooms")
    op.drop_table("properties")
    op.drop_table("vendors")
    op.drop_table("users")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS userrole")
    op.execute("DROP TYPE IF EXISTS propertytype")
    op.execute("DROP TYPE IF EXISTS tourcategory")
    op.execute("DROP TYPE IF EXISTS tourdifficulty")
    op.execute("DROP TYPE IF EXISTS bookingstatus")
    op.execute("DROP TYPE IF EXISTS blogpoststatus")
