from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings

# Optimized connection pool.
# NOTE: pool_size/max_overflow/pool_timeout are PostgreSQL/MySQL concepts and
# are rejected by SQLAlchemy when the dialect is SQLite (used in tests).
# Guard those kwargs so the same engine builder works in dev, prod and tests.
_engine_kwargs: dict = {
    "echo": settings.DEBUG,
    "pool_pre_ping": True,
    "pool_recycle": 1800,
}
if not settings.DATABASE_URL.startswith("sqlite"):
    _engine_kwargs.update(
        pool_size=20,
        max_overflow=30,
        pool_timeout=30,
    )
    if settings.DATABASE_URL.startswith("postgresql"):
        _engine_kwargs["connect_args"] = {
            "server_settings": {"application_name": "costa-rica-travel"}
        }

engine = create_async_engine(settings.DATABASE_URL, **_engine_kwargs)

# NullPool for serverless/lambda environments
# engine = create_async_engine(settings.DATABASE_URL, poolclass=NullPool)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except SQLAlchemyError:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Alias for FastAPI dependency injection
get_async_session = get_db