"""Add performance indexes for queries

Revision ID: 005_add_performance_indexes
Revises: 004_add_fulltext_search_room_availability
Create Date: 2025-01-15

"""
from typing import Sequence, Union
from alembic import op

revision: str = '005_add_performance_indexes'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Properties indexes
    op.create_index('idx_property_region', 'properties', ['region'])
    op.create_index('idx_property_base_price', 'properties', ['base_price'])
    op.create_index('idx_property_rating', 'properties', ['rating'])
    op.create_index('idx_property_created_at', 'properties', ['created_at'])
    op.create_index('idx_property_active_region', 'properties', ['is_active', 'region'])
    op.create_index('idx_property_active_price', 'properties', ['is_active', 'base_price'])

    # Tours indexes
    op.create_index('idx_tour_category', 'tours', ['category'])
    op.create_index('idx_tour_difficulty', 'tours', ['difficulty'])
    op.create_index('idx_tour_duration', 'tours', ['duration_hours'])
    op.create_index('idx_tour_created_at', 'tours', ['created_at'])
    op.create_index('idx_tour_active_category', 'tours', ['is_active', 'category'])

    # Destinations indexes
    op.create_index('idx_destination_region', 'destinations', ['region'])
    op.create_index('idx_destination_active', 'destinations', ['is_active'])

    # Bookings indexes
    op.create_index('idx_booking_status', 'bookings', ['status'])
    op.create_index('idx_booking_vendor_status', 'bookings', ['vendor_id', 'status'])
    op.create_index('idx_booking_vendor_created', 'bookings', ['vendor_id', 'created_at'])
    op.create_index('idx_booking_user_status', 'bookings', ['user_id', 'status'])
    op.create_index('idx_booking_payment_status', 'bookings', ['stripe_payment_status'])

    # Users indexes
    op.create_index('idx_user_email', 'users', ['email'])
    op.create_index('idx_user_role', 'users', ['role'])

    # Composite index for search queries
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_property_search_composite
        ON properties USING gin(to_tsvector('spanish', name || ' ' || COALESCE(short_description, '') || ' ' || COALESCE(description, '')))
    """)


def downgrade() -> None:
    op.drop_index('idx_property_region', 'properties')
    op.drop_index('idx_property_base_price', 'properties')
    op.drop_index('idx_property_rating', 'properties')
    op.drop_index('idx_property_created_at', 'properties')
    op.drop_index('idx_property_active_region', 'properties')
    op.drop_index('idx_property_active_price', 'properties')

    op.drop_index('idx_tour_category', 'tours')
    op.drop_index('idx_tour_difficulty', 'tours')
    op.drop_index('idx_tour_duration', 'tours')
    op.drop_index('idx_tour_created_at', 'tours')
    op.drop_index('idx_tour_active_category', 'tours')

    op.drop_index('idx_destination_region', 'destinations')
    op.drop_index('idx_destination_active', 'destinations')

    op.drop_index('idx_booking_status', 'bookings')
    op.drop_index('idx_booking_vendor_status', 'bookings')
    op.drop_index('idx_booking_vendor_created', 'bookings')
    op.drop_index('idx_booking_user_status', 'bookings')
    op.drop_index('idx_booking_payment_status', 'bookings')

    op.drop_index('idx_user_email', 'users')
    op.drop_index('idx_user_role', 'users')

    op.execute("DROP INDEX IF EXISTS idx_property_search_composite")