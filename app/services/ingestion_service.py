from typing import List, Dict, Any
from datetime import datetime
from bs4 import BeautifulSoup
import re

from app.services.graph_service import graph_service
from app.services.storage_service import storage_service
from app.database import SessionLocal
from app.models.models import Caso, Adjunto


class IngestionService:
    """Servicio para ingesta de correos y creación de casos"""

    async def process_inbox(self) -> Dict[str, Any]:
        """Procesar buzón de entrada"""
        results = {
            "processed": 0,
            "created": 0,
            "errors": 0,
            "messages": []
        }

        try:
            # Obtener mensajes no leídos
            messages = await graph_service.get_messages(
                folder="inbox",
                top=50,
                filter_query="isRead eq false"
            )

            results["processed"] = len(messages)

            for message in messages:
                try:
                    await self.process_message(message)
                    results["created"] += 1
                except Exception as e:
                    results["errors"] += 1
                    results["messages"].append(f"Error procesando mensaje {message['id']}: {str(e)}")

            return results

        except Exception as e:
            results["errors"] += 1
            results["messages"].append(f"Error general: {str(e)}")
            return results

    async def process_message(self, message: Dict[str, Any]) -> Caso:
        """Procesar un mensaje individual y crear caso"""
        db = SessionLocal()

        try:
            # Extraer información del mensaje
            subject = message.get("subject", "Sin asunto")
            body = message.get("body", {}).get("content", "")
            from_email = message.get("from", {}).get("emailAddress", {}).get("address", "")
            received_datetime = message.get("receivedDateTime")

            # Limpiar HTML del body
            clean_body = self.clean_html(body)

            # Determinar tipo de PQR desde el asunto
            tipo = self.extract_tipo_pqr(subject)

            # Crear caso
            from app.services.caso_service import create_caso
            from app.schemas.caso import CasoCreate

            caso_data = CasoCreate(
                tipo=tipo,
                asunto=subject,
                descripcion=clean_body,
                email_origen=from_email,
                prioridad="media"
            )

            caso = create_caso(db, caso_data)

            # Procesar adjuntos si existen
            if message.get("hasAttachments"):
                await self.process_attachments(message["id"], caso.id, db)

            # Marcar mensaje como leído
            await graph_service.mark_as_read(message["id"])

            db.commit()
            return caso

        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    async def process_attachments(self, message_id: str, caso_id: int, db) -> List[Adjunto]:
        """Procesar adjuntos de un mensaje"""
        attachments = await graph_service.get_message_attachments(message_id)
        adjuntos = []

        for attachment in attachments:
            if attachment.get("@odata.type") == "#microsoft.graph.fileAttachment":
                # Guardar adjunto
                file_path = storage_service.save_attachment(
                    attachment.get("contentBytes"),
                    attachment.get("name"),
                    caso_id
                )

                # Crear registro en BD
                db_adjunto = Adjunto(
                    caso_id=caso_id,
                    nombre_archivo=attachment.get("name"),
                    ruta_archivo=file_path,
                    tipo_mime=attachment.get("contentType"),
                    tamano=attachment.get("size")
                )
                db.add(db_adjunto)
                adjuntos.append(db_adjunto)

        return adjuntos

    def clean_html(self, html_content: str) -> str:
        """Limpiar contenido HTML y extraer texto"""
        soup = BeautifulSoup(html_content, "html.parser")
        text = soup.get_text(separator="\n")
        # Eliminar líneas vacías múltiples
        text = re.sub(r'\n\s*\n', '\n\n', text)
        return text.strip()

    def extract_tipo_pqr(self, subject: str) -> str:
        """Extraer tipo de PQR desde el asunto"""
        subject_lower = subject.lower()

        if any(word in subject_lower for word in ["queja", "inconformidad", "problema"]):
            return "queja"
        elif any(word in subject_lower for word in ["reclamo", "reclamación", "devolucion"]):
            return "reclamo"
        else:
            return "peticion"


ingestion_service = IngestionService()
