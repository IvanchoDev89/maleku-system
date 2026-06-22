"""enrich destinations table with rich travel content fields

Adds 20+ new columns to the destinations table for enriched travel
content: geography hierarchy (country -> canton -> district),
coordinates, practical info (language, currency, timezone, visa),
media (videos, featured_photo), SEO metadata, and more.

Revision ID: 007
Revises: 006
Create Date: 2026-06-18

"""

from typing import Union, Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "007"
down_revision: Union[str, None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _column_exists(table: str, column: str) -> bool:
    conn = op.get_bind()
    row = conn.execute(
        sa.text(
            "SELECT 1 FROM information_schema.columns "
            "WHERE table_name = :t AND column_name = :c"
        ),
        {"t": table, "c": column},
    ).first()
    return row is not None


def _index_exists(name: str) -> bool:
    conn = op.get_bind()
    row = conn.execute(
        sa.text("SELECT 1 FROM pg_indexes WHERE indexname = :n"),
        {"n": name},
    ).first()
    return row is not None


def upgrade() -> None:
    # ── Geographic hierarchy ──────────────────────────────────
    if not _column_exists("destinations", "country"):
        op.add_column(
            "destinations",
            sa.Column(
                "country", sa.String(100), server_default="Costa Rica", nullable=False
            ),
        )
    if not _column_exists("destinations", "canton"):
        op.add_column(
            "destinations",
            sa.Column("canton", sa.String(100), nullable=True),
        )
    if not _column_exists("destinations", "district"):
        op.add_column(
            "destinations",
            sa.Column("district", sa.String(100), nullable=True),
        )

    # ── Coordinates ───────────────────────────────────────────
    if not _column_exists("destinations", "latitude"):
        op.add_column(
            "destinations",
            sa.Column("latitude", sa.Float, nullable=True),
        )
    if not _column_exists("destinations", "longitude"):
        op.add_column(
            "destinations",
            sa.Column("longitude", sa.Float, nullable=True),
        )
    if not _column_exists("destinations", "zoom"):
        op.add_column(
            "destinations",
            sa.Column("zoom", sa.Integer, server_default="10"),
        )

    # ── Enriched travel content ───────────────────────────────
    for col in (
        "culture",
        "gastronomy",
        "history",
        "weather_info",
        "getting_there",
        "local_tips",
        "safety_info",
    ):
        if not _column_exists("destinations", col):
            op.add_column(
                "destinations",
                sa.Column(col, sa.Text, nullable=True),
            )

    # ── Practical information ─────────────────────────────────
    if not _column_exists("destinations", "language"):
        op.add_column(
            "destinations",
            sa.Column("language", sa.String(100), nullable=True),
        )
    if not _column_exists("destinations", "currency"):
        op.add_column(
            "destinations",
            sa.Column("currency", sa.String(100), nullable=True),
        )
    if not _column_exists("destinations", "timezone"):
        op.add_column(
            "destinations",
            sa.Column("timezone", sa.String(50), nullable=True),
        )
    if not _column_exists("destinations", "phone_code"):
        op.add_column(
            "destinations",
            sa.Column("phone_code", sa.String(10), nullable=True),
        )
    if not _column_exists("destinations", "visa_info"):
        op.add_column(
            "destinations",
            sa.Column("visa_info", sa.Text, nullable=True),
        )
    if not _column_exists("destinations", "emergency_numbers"):
        op.add_column(
            "destinations",
            sa.Column(
                "emergency_numbers",
                postgresql.JSON,
                server_default=sa.text("'[]'::json"),
            ),
        )

    # ── Media ─────────────────────────────────────────────────
    if not _column_exists("destinations", "videos"):
        op.add_column(
            "destinations",
            sa.Column("videos", postgresql.JSON, server_default=sa.text("'[]'::json")),
        )
    if not _column_exists("destinations", "featured_photo"):
        op.add_column(
            "destinations",
            sa.Column("featured_photo", sa.String(500), nullable=True),
        )

    # ── SEO ───────────────────────────────────────────────────
    if not _column_exists("destinations", "seo_title"):
        op.add_column(
            "destinations",
            sa.Column("seo_title", sa.String(70), nullable=True),
        )
    if not _column_exists("destinations", "seo_description"):
        op.add_column(
            "destinations",
            sa.Column("seo_description", sa.String(160), nullable=True),
        )
    if not _column_exists("destinations", "seo_keywords"):
        op.add_column(
            "destinations",
            sa.Column(
                "seo_keywords", postgresql.JSON, server_default=sa.text("'[]'::json")
            ),
        )

    # ── New indexes (idempotent) ──────────────────────────────
    for idx in [
        ("idx_destination_province", ["province"]),
        ("idx_destination_canton", ["canton"]),
        ("idx_destination_country", ["country"]),
        ("idx_destination_order", ["order"]),
    ]:
        name, cols = idx
        if not _index_exists(name):
            op.create_index(name, "destinations", cols)

    if not _index_exists("idx_destination_featured"):
        op.create_index(
            "idx_destination_featured",
            "destinations",
            ["is_featured", "is_active"],
        )


def downgrade() -> None:
    # Drop indexes first
    for name in [
        "idx_destination_featured",
        "idx_destination_order",
        "idx_destination_country",
        "idx_destination_canton",
        "idx_destination_province",
    ]:
        if _index_exists(name):
            op.drop_index(name, table_name="destinations")

    # Drop columns (reverse order)
    cols_to_drop = [
        "seo_keywords",
        "seo_description",
        "seo_title",
        "featured_photo",
        "videos",
        "emergency_numbers",
        "visa_info",
        "phone_code",
        "timezone",
        "currency",
        "language",
        "safety_info",
        "local_tips",
        "getting_there",
        "weather_info",
        "history",
        "gastronomy",
        "culture",
        "zoom",
        "longitude",
        "latitude",
        "district",
        "canton",
        "country",
    ]
    for col in cols_to_drop:
        if _column_exists("destinations", col):
            op.drop_column("destinations", col)
