"""
Contact form endpoint.
Receives contact messages and logs them.
"""
from fastapi import APIRouter
from pydantic import BaseModel, EmailStr, Field
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Contact"])


class ContactRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    email: EmailStr
    subject: str = Field(..., min_length=3, max_length=300)
    message: str = Field(..., min_length=10, max_length=5000)


@router.post("/contact", summary="Submit contact form",
             description="Receives a contact form submission and logs it.")
async def submit_contact(data: ContactRequest):
    logger.info(
        "CONTACT FORM: name=%s email=%s subject=%s message=%s",
        data.name, data.email, data.subject, data.message[:100]
    )
    return {
        "success": True,
        "message": "Mensaje recibido correctamente. Te contactaremos pronto."
    }
