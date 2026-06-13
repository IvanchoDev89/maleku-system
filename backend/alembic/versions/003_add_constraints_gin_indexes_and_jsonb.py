"""add constraints gin indexes and jsonb

Revision ID: 003
Revises: 002
Create Date: 2026-04-30
"""

from typing import Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "003"
down_revision: Union[str, None] = "002"


def upgrade() -> None:
    # Conversations & Messages - Soft Deletes
    op.add_column(
        "conversations", sa.Column("deleted_at", sa.DateTime(), nullable=True)
    )
    op.create_index("idx_conv_deleted", "conversations", ["deleted_at"])

    op.add_column("messages", sa.Column("deleted_at", sa.DateTime(), nullable=True))
    op.create_index("idx_message_deleted", "messages", ["deleted_at"])

    # GIN Indexes for JSONB search
    op.create_index(
        "idx_property_amenities_gin",
        "properties",
        ["amenities"],
        postgresql_using="gin",
    )
    op.create_index(
        "idx_property_features_gin", "properties", ["features"], postgresql_using="gin"
    )
    op.create_index(
        "idx_vehicle_features_gin", "vehicles", ["features"], postgresql_using="gin"
    )
    op.create_index(
        "idx_boat_features_gin", "boats", ["features"], postgresql_using="gin"
    )
    op.create_index(
        "idx_transport_features_gin",
        "transportation",
        ["features"],
        postgresql_using="gin",
    )
    op.create_index(
        "idx_tour_included_gin", "tours", ["included"], postgresql_using="gin"
    )

    # CHECK Constraints
    op.create_check_constraint(
        "chk_property_rating", "properties", sa.text("rating >= 0 AND rating <= 5")
    )
    op.create_check_constraint(
        "chk_property_min_guests", "properties", sa.text("min_guests > 0")
    )
    op.create_check_constraint(
        "chk_property_capacity", "properties", sa.text("max_guests >= min_guests")
    )
    op.create_check_constraint(
        "chk_review_rating_range", "reviews", sa.text("rating >= 1 AND rating <= 5")
    )
    op.create_check_constraint("chk_booking_guests", "bookings", sa.text("guests > 0"))
    op.create_check_constraint(
        "chk_booking_amount_positive", "bookings", sa.text("total_amount >= 0")
    )

    # Marketing JSONB conversions
    tables_jsonb = [
        ("email_campaigns", "recipient_list"),
        ("email_campaigns", "segment_criteria"),
        ("email_templates", "available_variables"),
        ("email_logs", "clicked_links"),
        ("marketing_automations", "steps"),
        ("marketing_automations", "trigger_criteria"),
        ("email_preferences", "vendor_preferences"),
        ("email_preferences", "categories"),
    ]

    for table, column in tables_jsonb:
        op.alter_column(
            table, column, type_=postgresql.JSONB(), postgresql_using=f"{column}::jsonb"
        )

    # Booking availability index
    op.create_index(
        "idx_booking_availability",
        "bookings",
        ["property_id", "room_id", "check_in", "check_out"],
        postgresql_where=sa.text("deleted_at IS NULL"),
    )


def downgrade() -> None:
    # Reverse JSONB to JSON
    tables = [
        ("email_preferences", "categories"),
        ("email_preferences", "vendor_preferences"),
        ("marketing_automations", "trigger_criteria"),
        ("marketing_automations", "steps"),
        ("email_logs", "clicked_links"),
        ("email_templates", "available_variables"),
        ("email_campaigns", "segment_criteria"),
        ("email_campaigns", "recipient_list"),
    ]

    for table, column in tables:
        op.alter_column(
            table, column, type_=postgresql.JSON(), postgresql_using=f"{column}::json"
        )

    # Remove constraints
    op.drop_constraint("chk_booking_amount_positive", "bookings", type_="check")
    op.drop_constraint("chk_booking_guests", "bookings", type_="check")
    op.drop_constraint("chk_review_rating_range", "reviews", type_="check")
    op.drop_constraint("chk_property_capacity", "properties", type_="check")
    op.drop_constraint("chk_property_min_guests", "properties", type_="check")
    op.drop_constraint("chk_property_rating", "properties", type_="check")

    # Remove indexes
    op.drop_index("idx_booking_availability", table_name="bookings")
    op.drop_index("idx_tour_included_gin", table_name="tours")
    op.drop_index("idx_transport_features_gin", table_name="transportation")
    op.drop_index("idx_boat_features_gin", table_name="boats")
    op.drop_index("idx_vehicle_features_gin", table_name="vehicles")
    op.drop_index("idx_property_features_gin", table_name="properties")
    op.drop_index("idx_property_amenities_gin", table_name="properties")

    # Remove soft delete columns
    op.drop_index("idx_message_deleted", table_name="messages")
    op.drop_column("messages", "deleted_at")
    op.drop_index("idx_conv_deleted", table_name="conversations")
    op.drop_column("conversations", "deleted_at")
