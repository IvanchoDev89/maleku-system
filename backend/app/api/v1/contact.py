"""
Contact form endpoint.
Receives contact messages and logs them.
"""

from fastapi import APIRouter, Request
from pydantic import BaseModel, EmailStr, Field
from slowapi import Limiter
from slowapi.util import get_remote_address
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Contact"])
limiter = Limiter(key_func=get_remote_address, enabled=settings.ENVIRONMENT != "test")


class ContactRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    email: EmailStr
    subject: str = Field(..., min_length=3, max_length=300)
    message: str = Field(..., min_length=10, max_length=5000)


@router.post(
    "/contact",
    summary="Submit contact form",
    description="Receives a contact form submission and logs it. Rate limited to 5/minute/IP.",
)
@limiter.limit("5/minute")
async def submit_contact(request: Request, data: ContactRequest):
    logger.info(
        "CONTACT FORM: name=%s email=%s subject=%s message=%s",
        data.name,
        data.email,
        data.subject,
        data.message[:100],
    )
    return {
        "success": True,
        "message": "Mensaje recibido correctamente. Te contactaremos pronto.",
    }
