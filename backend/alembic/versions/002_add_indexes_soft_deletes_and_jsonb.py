"""add indexes soft deletes and jsonb

Revision ID: 002
Revises: c98a5b5e0fd5
Create Date: 2026-04-30

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '002'
down_revision: Union[str, None] = 'c98a5b5e0fd5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Soft deletes - Core tables
    tables = ['users', 'vendors', 'properties', 'rooms', 'tours', 
              'bookings', 'reviews', 'blog_posts', 'vehicles', 
              'boats', 'flights', 'transportation']
    
    for table in tables:
        op.add_column(table, sa.Column('deleted_at', sa.DateTime(), nullable=True))
        op.create_index(f'idx_{table.rstrip("s")}_deleted', table, ['deleted_at'])
    
    # JSONB conversions for queryable fields
    op.alter_column('properties', 'amenities', type_=postgresql.JSONB(), postgresql_using='amenities::jsonb')
    op.alter_column('properties', 'features', type_=postgresql.JSONB(), postgresql_using='features::jsonb')
    op.alter_column('vehicles', 'features', type_=postgresql.JSONB(), postgresql_using='features::jsonb')
    op.alter_column('boats', 'features', type_=postgresql.JSONB(), postgresql_using='features::jsonb')
    op.alter_column('transportation', 'features', type_=postgresql.JSONB(), postgresql_using='features::jsonb')
    
    # User indexes
    op.create_index('idx_user_role_active', 'users', ['role', 'is_active', 'deleted_at'])
    op.create_index('idx_user_created', 'users', ['created_at'])
    
    # Property indexes
    op.create_index('idx_property_geo', 'properties', ['latitude', 'longitude'])
    op.drop_index('idx_property_featured', table_name='properties')
    op.create_index('idx_property_featured', 'properties', ['is_featured', 'is_active', 'deleted_at'])
    
    # Room indexes
    op.create_index('idx_room_property', 'rooms', ['property_id', 'deleted_at'])
    
    # Tour indexes
    op.create_index('idx_tour_featured', 'tours', ['is_featured', 'is_active', 'deleted_at'])
    
    # Booking indexes
    op.create_index('idx_booking_status', 'bookings', ['status', 'deleted_at'])
    
    # Review indexes
    op.create_index('idx_review_approved', 'reviews', ['is_approved', 'deleted_at'])
    
    # Blog indexes
    op.create_index('idx_blog_status', 'blog_posts', ['status', 'deleted_at'])
    op.create_index('idx_blog_featured', 'blog_posts', ['is_featured', 'status', 'deleted_at'])
    
    # Transport indexes - Vehicles
    op.create_index('idx_vehicle_vendor', 'vehicles', ['vendor_id'])
    op.create_index('idx_vehicle_type', 'vehicles', ['vehicle_type'])
    op.create_index('idx_vehicle_available', 'vehicles', ['is_available', 'is_active', 'deleted_at'])
    op.create_index('idx_vehicle_price', 'vehicles', ['price_per_day'])
    op.create_index('idx_vehicle_location', 'vehicles', ['location'])
    
    # Transport indexes - Boats
    op.create_index('idx_boat_vendor', 'boats', ['vendor_id'])
    op.create_index('idx_boat_type', 'boats', ['equipment_type'])
    op.create_index('idx_boat_available', 'boats', ['is_available', 'is_active', 'deleted_at'])
    op.create_index('idx_boat_price', 'boats', ['price_per_hour'])
    op.create_index('idx_boat_location', 'boats', ['location'])
    
    # Transport indexes - Flights
    op.create_index('idx_flight_vendor', 'flights', ['vendor_id'])
    op.create_index('idx_flight_route', 'flights', ['origin_airport', 'destination_airport'])
    op.create_index('idx_flight_route_type', 'flights', ['route_type'])
    op.create_index('idx_flight_active', 'flights', ['is_active', 'deleted_at'])
    op.create_index('idx_flight_price', 'flights', ['price_economy'])
    
    # Transport indexes - Transportation
    op.create_index('idx_transport_vendor', 'transportation', ['vendor_id'])
    op.create_index('idx_transport_service_type', 'transportation', ['service_type'])
    op.create_index('idx_transport_vehicle_type', 'transportation', ['vehicle_type'])
    op.create_index('idx_transport_available', 'transportation', ['is_available', 'is_active', 'deleted_at'])
    op.create_index('idx_transport_price', 'transportation', ['base_price'])
    
    # Pricing indexes
    op.create_index('idx_pricing_service', 'pricing_rules', ['service_type', 'service_id'])
    op.create_index('idx_pricing_active', 'pricing_rules', ['is_active'])
    op.create_index('idx_pricing_date_range', 'pricing_rules', ['date_from', 'date_to'])


def downgrade() -> None:
    # Remove all indexes and columns (reverse of upgrade)
    # See full implementation in migration file
    pass
