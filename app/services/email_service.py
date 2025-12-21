from typing import List, Optional
import httpx
from datetime import datetime

from app.config import settings
from app.schemas.correo import EmailMessage, EmailResponse
from app.core.exceptions import EmailException


class EmailService:
    """Servicio para envío de correos"""

    async def send_email(self, email: EmailMessage) -> EmailResponse:
        """Enviar correo electrónico"""
        try:
            # Aquí iría la lógica real de envío usando Microsoft Graph API
            # o cualquier otro servicio de correo

            # Simulación por ahora
            print(f"Enviando correo a: {email.to}")
            print(f"Asunto: {email.subject}")

            return EmailResponse(
                success=True,
                message_id=f"msg_{datetime.now().timestamp()}"
            )
        except Exception as e:
            raise EmailException(f"Error enviando correo: {str(e)}")

    async def send_caso_notification(
        self,
        to: List[str],
        numero_caso: str,
        asunto: str,
        tipo_notificacion: str = "nuevo"
    ) -> EmailResponse:
        """Enviar notificación de caso"""
        subject_map = {
            "nuevo": f"Nuevo caso {numero_caso}: {asunto}",
            "actualizado": f"Caso {numero_caso} actualizado",
            "escalado": f"Caso {numero_caso} ha sido escalado",
            "cerrado": f"Caso {numero_caso} cerrado"
        }

        body = f"""
        <html>
        <body>
            <h2>{subject_map.get(tipo_notificacion, 'Notificación')}</h2>
            <p><strong>Número de caso:</strong> {numero_caso}</p>
            <p><strong>Asunto:</strong> {asunto}</p>
            <p>Por favor, ingrese al sistema para más detalles.</p>
        </body>
        </html>
        """

        email = EmailMessage(
            to=to,
            subject=subject_map.get(tipo_notificacion, "Notificación de caso"),
            body=body
        )

        return await self.send_email(email)

    async def send_escalation_notification(
        self,
        to: List[str],
        numero_caso: str,
        nivel: int,
        motivo: str
    ) -> EmailResponse:
        """Enviar notificación de escalamiento"""
        subject = f"Escalamiento Nivel {nivel} - Caso {numero_caso}"
        body = f"""
        <html>
        <body>
            <h2>Escalamiento de Caso</h2>
            <p><strong>Número de caso:</strong> {numero_caso}</p>
            <p><strong>Nivel de escalamiento:</strong> {nivel}</p>
            <p><strong>Motivo:</strong> {motivo}</p>
            <p>Este caso requiere atención inmediata.</p>
        </body>
        </html>
        """

        email = EmailMessage(
            to=to,
            subject=subject,
            body=body
        )

        return await self.send_email(email)


email_service = EmailService()
