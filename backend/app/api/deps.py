from typing import AsyncGenerator
from fastapi import BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def get_background_tasks(request: Request) -> BackgroundTasks:
    return request.state.background_tasks
