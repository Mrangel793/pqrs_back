from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class EmailMessage(BaseModel):
    """Schema para mensaje de correo"""
    to: List[EmailStr]
    subject: str
    body: str
    cc: Optional[List[EmailStr]] = None
    bcc: Optional[List[EmailStr]] = None
    attachments: Optional[List[str]] = None


class EmailResponse(BaseModel):
    """Schema de respuesta de envío de correo"""
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None


class InboxMessage(BaseModel):
    """Schema para mensaje del buzón"""
    id: str
    subject: str
    from_email: str
    received_datetime: datetime
    body_preview: str
    has_attachments: bool
    is_read: bool
