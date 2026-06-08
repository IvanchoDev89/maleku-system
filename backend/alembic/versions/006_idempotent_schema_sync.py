"""idempotent schema sync: room_availability, FTS indexes, CHECKs, GIN JSONB

This migration reconciles the live DB with the model definitions.
The earlier chain (003-005) was bypassed when the DB was created
via ``Base.metadata.create_all`` (which doesn't reliably emit
``Index(text=...)`` GIN expressions or named ``CheckConstraint``s),
and ``alembic stamp head`` was run to mark the schema as current.

Every step is wrapped with ``IF NOT EXISTS`` checks so re-running
``alembic upgrade head`` on a fresh DB seeded by create_all is safe.

Revision ID: 006
Revises: 5c57a60106d5
Create Date: 2026-06-07

"""
from typing import Union, Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = '006'
down_revision: Union[str, None] = '5c57a60106d5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _index_exists(name: str) -> bool:
    conn = op.get_bind()
    row = conn.execute(
        sa.text("SELECT 1 FROM pg_indexes WHERE indexname = :n"),
        {"n": name},
    ).first()
    return row is not None


def _constraint_exists(name: str) -> bool:
    conn = op.get_bind()
    row = conn.execute(
        sa.text("SELECT 1 FROM pg_constraint WHERE conname = :n"),
        {"n": name},
    ).first()
    return row is not None


def _table_exists(name: str) -> bool:
    conn = op.get_bind()
    row = conn.execute(
        sa.text("SELECT 1 FROM information_schema.tables WHERE table_name = :n"),
        {"n": name},
    ).first()
    return row is not None


def _safe_create_check(name: str, table: str, expr: str) -> None:
    if _constraint_exists(name):
        return
    op.create_check_constraint(name, table, sa.text(expr))


def _safe_create_index(name: str, table: str, columns, *, postgresql_using: str | None = None) -> None:
    if _index_exists(name):
        return
    if postgresql_using:
        op.create_index(name, table, columns, postgresql_using=postgresql_using)
    else:
        op.create_index(name, table, columns)


def upgrade() -> None:
    # ------------------------------------------------------------------
    # 1. Room availability (was never created — bug in 004 had notes:Float)
    # ------------------------------------------------------------------
    if not _table_exists('room_availability'):
        op.create_table(
            'room_availability',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('room_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('rooms.id', ondelete='CASCADE'), nullable=False),
            sa.Column('date', sa.Date(), nullable=False),
            sa.Column('is_available', sa.Boolean(), server_default=sa.text('true'), nullable=False),
            sa.Column('price_override', sa.Numeric(10, 2), nullable=True),
            sa.Column('min_stay', sa.Integer(), nullable=True),
            sa.Column('max_stay', sa.Integer(), nullable=True),
            sa.Column('close_to_arrival', sa.Boolean(), server_default=sa.text('false')),
            sa.Column('close_to_departure', sa.Boolean(), server_default=sa.text('false')),
            sa.Column('notes', sa.Text(), nullable=True),  # was Float() in 004 — fixed
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        )

    _safe_create_index('idx_room_availability_unique', 'room_availability', ['room_id', 'date'], postgresql_using=None)
    # mark unique separately if not exists
    conn = op.get_bind()
    if not _index_exists('idx_room_availability_unique'):
        op.create_index('idx_room_availability_unique', 'room_availability', ['room_id', 'date'], unique=True)
    _safe_create_index('idx_room_availability_date_range', 'room_availability', ['room_id', 'date', 'is_available'])
    _safe_create_index('idx_room_availability_status', 'room_availability', ['is_available', 'date'])
    _safe_create_index('idx_room_availability_date_lookup', 'room_availability', ['date', 'is_available', 'room_id'])

    # ------------------------------------------------------------------
    # 2. Full-text search indexes (Spanish) — match the model Index(text=...)
    # ------------------------------------------------------------------
    if not _index_exists('idx_property_fts'):
        op.execute(
            "CREATE INDEX idx_property_fts ON properties USING gin ("
            "to_tsvector('spanish', COALESCE(name, '') || ' ' || "
            "COALESCE(short_description, '') || ' ' || "
            "COALESCE(description, '') || ' ' || "
            "COALESCE(city, '') || ' ' || COALESCE(region, '')))"
        )
    if not _index_exists('idx_tour_fts'):
        op.execute(
            "CREATE INDEX idx_tour_fts ON tours USING gin ("
            "to_tsvector('spanish', COALESCE(name, '') || ' ' || "
            "COALESCE(description, '') || ' ' || COALESCE(location, '')))"
        )
    if not _index_exists('idx_blog_fts'):
        op.execute(
            "CREATE INDEX idx_blog_fts ON blog_posts USING gin ("
            "to_tsvector('spanish', COALESCE(title, '') || ' ' || "
            "COALESCE(content, '') || ' ' || COALESCE(excerpt, '')))"
        )

    # ------------------------------------------------------------------
    # 3. GIN JSONB indexes (003 declared but not applied)
    # ------------------------------------------------------------------
    gin_indexes = [
        ('idx_property_amenities_gin', 'properties', 'amenities'),
        ('idx_property_features_gin', 'properties', 'features'),
        ('idx_vehicle_features_gin', 'vehicles', 'features'),
        ('idx_boat_features_gin', 'boats', 'features'),
        ('idx_transport_features_gin', 'transportation', 'features'),
        ('idx_tour_included_gin', 'tours', 'included'),
    ]
    for name, table, col in gin_indexes:
        _safe_create_index(name, table, [col], postgresql_using='gin')

    # ------------------------------------------------------------------
    # 4. CHECK constraints from models
    # ------------------------------------------------------------------
    _safe_create_check('chk_property_rating', 'properties', 'rating >= 0 AND rating <= 5')
    _safe_create_check('chk_property_min_guests', 'properties', 'min_guests > 0')
    _safe_create_check('chk_property_capacity', 'properties', 'max_guests >= min_guests')
    _safe_create_check('chk_property_base_price', 'properties', 'base_price >= 0')
    _safe_create_check('chk_property_latitude', 'properties', 'latitude IS NULL OR (latitude >= -90 AND latitude <= 90)')
    _safe_create_check('chk_property_longitude', 'properties', 'longitude IS NULL OR (longitude >= -180 AND longitude <= 180)')

    _safe_create_check('chk_tour_rating', 'tours', 'rating >= 0 AND rating <= 5')
    _safe_create_check('chk_tour_price_positive', 'tours', 'price >= 0')
    _safe_create_check('chk_tour_duration_positive', 'tours', 'duration_hours > 0')
    _safe_create_check('chk_tour_min_age', 'tours', 'min_age >= 0')
    _safe_create_check('chk_tour_group_size', 'tours', 'max_group_size > 0')

    _safe_create_check('chk_booking_guests', 'bookings', 'guests > 0')
    _safe_create_check('chk_booking_amount_positive', 'bookings', 'total_amount >= 0')
    _safe_create_check('chk_review_rating_range', 'reviews', 'rating >= 1 AND rating <= 5')


def downgrade() -> None:
    if _constraint_exists('chk_review_rating_range'):
        op.drop_constraint('chk_review_rating_range', 'reviews', type_='check')
    if _constraint_exists('chk_booking_amount_positive'):
        op.drop_constraint('chk_booking_amount_positive', 'bookings', type_='check')
    if _constraint_exists('chk_booking_guests'):
        op.drop_constraint('chk_booking_guests', 'bookings', type_='check')
    for name in [
        'chk_tour_rating', 'chk_tour_price_positive', 'chk_tour_duration_positive',
        'chk_tour_min_age', 'chk_tour_group_size',
        'chk_property_rating', 'chk_property_min_guests', 'chk_property_capacity',
        'chk_property_base_price', 'chk_property_latitude', 'chk_property_longitude',
    ]:
        table = 'tours' if name.startswith('chk_tour_') else 'properties'
        if _constraint_exists(name):
            op.drop_constraint(name, table, type_='check')

    for name in [
        'idx_tour_included_gin', 'idx_transport_features_gin', 'idx_boat_features_gin',
        'idx_vehicle_features_gin', 'idx_property_features_gin', 'idx_property_amenities_gin',
    ]:
        if _index_exists(name):
            op.drop_index(name)

    for name in ['idx_blog_fts', 'idx_tour_fts', 'idx_property_fts']:
        if _index_exists(name):
            op.execute(f"DROP INDEX {name}")

    if _table_exists('room_availability'):
        op.drop_table('room_availability')
