from fastapi import BackgroundTasks
from app.core.logging import get_logger

logger = get_logger(__name__)


class TaskQueue:
    def __init__(self):
        self._background_tasks: BackgroundTasks | None = None

    def init(self, background_tasks: BackgroundTasks):
        self._background_tasks = background_tasks

    def add_task(self, func, *args, **kwargs):
        if self._background_tasks:
            self._background_tasks.add_task(func, *args, **kwargs)
        else:
            logger.warning("BackgroundTasks not initialized — running synchronously")

    async def send_email_async(self, email_func, *args, **kwargs):
        try:
            result = await email_func(*args, **kwargs)
            logger.info(f"Background email sent: {result.get('id', 'unknown')}")
        except Exception as e:
            logger.error(f"Background email failed: {e}")

    async def log_audit_async(self, audit_service, action: str, entity_type: str, entity_id: str, user_id: str, details: dict | None = None):
        try:
            await audit_service.log_action(
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                user_id=user_id,
                details=details
            )
        except Exception as e:
            logger.error(f"Background audit log failed: {e}")


task_queue = TaskQueue()
