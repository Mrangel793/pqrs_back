from fastapi import APIRouter, Depends
from typing import List

from app.api.deps import get_current_user_dep
from app.schemas.correo import EmailMessage, EmailResponse, InboxMessage
from app.services.email_service import email_service
from app.services.graph_service import graph_service

router = APIRouter()


@router.post("/send", response_model=EmailResponse)
async def send_email(
    email: EmailMessage,
    current_user = Depends(get_current_user_dep)
):
    """Enviar correo electrónico"""
    result = await email_service.send_email(email)
    return result


@router.get("/inbox", response_model=List[InboxMessage])
async def get_inbox_messages(
    top: int = 10,
    current_user = Depends(get_current_user_dep)
):
    """Obtener mensajes del buzón de entrada"""
    messages = await graph_service.get_messages(folder="inbox", top=top)

    return [
        InboxMessage(
            id=msg["id"],
            subject=msg.get("subject", ""),
            from_email=msg.get("from", {}).get("emailAddress", {}).get("address", ""),
            received_datetime=msg.get("receivedDateTime"),
            body_preview=msg.get("bodyPreview", ""),
            has_attachments=msg.get("hasAttachments", False),
            is_read=msg.get("isRead", False)
        )
        for msg in messages
    ]
