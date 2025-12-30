import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.config import settings
from app.core.exceptions import EmailException


class GraphService:
    """Servicio para interactuar con Microsoft Graph API"""

    def __init__(self):
        self.client_id = settings.MICROSOFT_CLIENT_ID
        self.client_secret = settings.MICROSOFT_CLIENT_SECRET
        self.tenant_id = settings.MICROSOFT_TENANT_ID
        self.mailbox = settings.MAILBOX_ADDRESS
        self.access_token = None

    async def get_access_token(self) -> str:
        """Obtener token de acceso de Microsoft Graph"""
        url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"

        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "https://graph.microsoft.com/.default",
            "grant_type": "client_credentials"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=data)
            if response.status_code == 200:
                self.access_token = response.json()["access_token"]
                return self.access_token
            else:
                raise EmailException(f"Error obteniendo token de acceso: {response.status_code} - {response.text}")

    async def get_messages(
        self,
        folder: str = "inbox",
        top: int = 10,
        filter_query: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Obtener mensajes del buzón"""
        if not self.access_token:
            await self.get_access_token()

        url = f"https://graph.microsoft.com/v1.0/users/{self.mailbox}/mailFolders/{folder}/messages"
        params = {"$top": top}

        if filter_query:
            params["$filter"] = filter_query

        headers = {"Authorization": f"Bearer {self.access_token}"}

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)
            if response.status_code == 200:
                return response.json().get("value", [])
            else:
                raise EmailException(f"Error obteniendo mensajes: {response.status_code} - {response.text}")

    async def get_message_attachments(self, message_id: str) -> List[Dict[str, Any]]:
        """Obtener adjuntos de un mensaje"""
        if not self.access_token:
            await self.get_access_token()

        url = f"https://graph.microsoft.com/v1.0/users/{self.mailbox}/messages/{message_id}/attachments"
        headers = {"Authorization": f"Bearer {self.access_token}"}

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                return response.json().get("value", [])
            else:
                raise EmailException(f"Error obteniendo adjuntos: {response.status_code} - {response.text}")

    async def send_message(
        self,
        to: List[str],
        subject: str,
        body: str,
        cc: Optional[List[str]] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Enviar mensaje"""
        if not self.access_token:
            await self.get_access_token()

        url = f"https://graph.microsoft.com/v1.0/users/{self.mailbox}/sendMail"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        message = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "HTML",
                    "content": body
                },
                "toRecipients": [{"emailAddress": {"address": addr}} for addr in to]
            }
        }

        if cc:
            message["message"]["ccRecipients"] = [{"emailAddress": {"address": addr}} for addr in cc]

        if attachments:
            message["message"]["attachments"] = attachments

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=message)
            if response.status_code in [200, 202]:
                return {"success": True}
            else:
                raise EmailException(f"Error enviando mensaje: {response.text}")

    async def mark_as_read(self, message_id: str) -> bool:
        """Marcar mensaje como leído"""
        if not self.access_token:
            await self.get_access_token()

        url = f"https://graph.microsoft.com/v1.0/users/{self.mailbox}/messages/{message_id}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        data = {"isRead": True}

        async with httpx.AsyncClient() as client:
            response = await client.patch(url, headers=headers, json=data)
            return response.status_code == 200


graph_service = GraphService()
