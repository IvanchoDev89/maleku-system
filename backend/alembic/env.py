from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
import asyncio

from app.core.config import settings
from app.core.database import Base

# Import all models to register them with Base metadata
import app.models.user  # noqa: F401
import app.models.vendor  # noqa: F401
import app.models.destination  # noqa: F401
import app.models.property  # noqa: F401
import app.models.booking  # noqa: F401
import app.models.tour  # noqa: F401
import app.models.review  # noqa: F401
import app.models.blog  # noqa: F401
import app.models.vehicle  # noqa: F401
import app.models.boat  # noqa: F401
import app.models.flight  # noqa: F401
import app.models.transportation  # noqa: F401
import app.models.newsletter  # noqa: F401
import app.models.marketing  # noqa: F401
import app.models.audit  # noqa: F401
import app.models.chat  # noqa: F401
import app.models.planner  # noqa: F401
import app.models.pricing  # noqa: F401
import app.models.room_availability  # noqa: F401
import app.models.trip_planner  # noqa: F401
import app.models.content  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = settings.DATABASE_URL
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
