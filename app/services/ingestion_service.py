from typing import List, Dict, Any, Tuple
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
            "skipped": 0,
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
                    caso, created = await self.process_message(message)
                    if created:
                        results["created"] += 1
                    else:
                        results["skipped"] += 1
                except Exception as e:
                    results["errors"] += 1
                    results["messages"].append(f"Error procesando mensaje {message['id']}: {str(e)}")

            return results

        except Exception as e:
            results["errors"] += 1
            results["messages"].append(f"Error general: {str(e)}")
            return results

    async def process_message(self, message: Dict[str, Any]) -> Tuple[Caso, bool]:
        """Procesar un mensaje individual y crear caso"""
        db = SessionLocal()

        try:
            # Verificar si el mensaje ya fue procesado
            message_id = message.get("id")
            existing_caso = db.query(Caso).filter(Caso.correoHiloId == message_id).first()
            if existing_caso:
                return existing_caso, False

            # Extraer información del mensaje
            subject = message.get("subject", "Sin asunto")
            body = message.get("body", {}).get("content", "")
            from_email = message.get("from", {}).get("emailAddress", {}).get("address", "")
            from_name = message.get("from", {}).get("emailAddress", {}).get("name", from_email)
            received_datetime = message.get("receivedDateTime")
            to_email = message.get("toRecipients", [{}])[0].get("emailAddress", {}).get("address", "")

            # Parsear datos estructurados del correo (tabla HTML)
            parsed_data = self.parse_email_data(body)

            # Limpiar HTML del body
            clean_body = self.clean_html(body)

            # Determinar tipo de tramite desde el asunto o datos parseados
            tipo_tramite = parsed_data.get("tipoTramite") or self.extract_tipo_pqr(subject)

            # Extraer radicado del correo (tabla o texto)
            radicado = parsed_data.get("radicado") or self.extract_radicado(clean_body)
            if not radicado:
                radicado = self.generate_radicado(db)

            # Verificar si ya existe un caso con este radicado
            existing_caso_by_radicado = db.query(Caso).filter(Caso.radicado == radicado).first()
            if existing_caso_by_radicado:
                # Si el caso existe, actualizar el correoHiloId si es diferente
                if existing_caso_by_radicado.correoHiloId != message_id:
                    # Este es un correo adicional relacionado con el mismo radicado
                    # Podrías crear una entrada en FuenteCorreo aquí si lo deseas
                    pass
                return existing_caso_by_radicado, False

            # Parsear fechas del correo o usar valores por defecto
            fecha_recepcion = parsed_data.get("fechaRecepcion")
            if not fecha_recepcion:
                fecha_recepcion = datetime.fromisoformat(received_datetime.replace('Z', '+00:00')) if received_datetime else datetime.now()

            fecha_vencimiento = parsed_data.get("fechaVencimiento")
            if not fecha_vencimiento:
                fecha_vencimiento = self.calculate_due_date(fecha_recepcion, days=5)

            # Crear caso
            from app.services.caso_service import create_caso
            from app.schemas.caso import CasoCreate

            caso_data = CasoCreate(
                radicado=radicado,
                fechaRecepcion=fecha_recepcion,
                fechaVencimiento=fecha_vencimiento,
                peticionarioNombre=parsed_data.get("peticionarioNombre") or from_name,
                peticionarioCorreo=parsed_data.get("peticionarioCorreo") or from_email,
                detalleSolicitud=parsed_data.get("detalleSolicitud") or clean_body,
                tipoTramite=tipo_tramite,
                estadoCasoId=1,  # Estado "Nuevo"
                semaforoId=1,  # Semáforo por defecto
                destinatarioCorreo=to_email if to_email else from_email,
                correoHiloId=message_id,
                correoEnvioEstadoId=1  # Estado de envío inicial
            )

            caso = create_caso(db, caso_data)

            # Procesar adjuntos si existen
            if message.get("hasAttachments"):
                await self.process_attachments(message["id"], caso.id, db)

            # Marcar mensaje como leído
            await graph_service.mark_as_read(message["id"])

            db.commit()
            return caso, True

        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    async def process_attachments(self, message_id: str, caso_id, db) -> List[Adjunto]:
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
                    casoId=caso_id,
                    tipoAdjuntoId=1,  # Tipo por defecto (asegúrate que existe en tab_tipoadjunto)
                    messageIdOrigen=message_id,
                    nombreArchivo=attachment.get("name"),
                    mimeType=attachment.get("contentType", "application/octet-stream"),
                    tamanioBytes=attachment.get("size"),
                    rutaStorage=file_path
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

    def generate_radicado(self, db) -> str:
        """Generar radicado único basado en fecha y secuencia"""
        now = datetime.now()
        prefix = now.strftime("%Y%m%d")
        
        # Buscar el último radicado del día
        last_caso = db.query(Caso).filter(
            Caso.radicado.like(f"{prefix}%")
        ).order_by(Caso.radicado.desc()).first()
        
        if last_caso:
            # Extraer el número de secuencia y incrementar
            try:
                last_sequence = int(last_caso.radicado[-4:])
                sequence = last_sequence + 1
            except (ValueError, IndexError):
                sequence = 1
        else:
            sequence = 1
        
        # Formato: YYYYMMDD-NNNN
        return f"{prefix}-{sequence:04d}"

    def calculate_due_date(self, start_date: datetime, days: int = 5) -> datetime:
        """Calcular fecha de vencimiento excluyendo fines de semana"""
        from datetime import timedelta
        
        current_date = start_date
        days_added = 0
        
        while days_added < days:
            current_date = current_date + timedelta(days=1)
            
            # Si no es fin de semana (0=Lunes, 6=Domingo)
            if current_date.weekday() < 5:
                days_added += 1
        
        return current_date

    def parse_email_data(self, html_content: str) -> Dict[str, Any]:
        """Parsear datos estructurados desde tabla HTML del correo"""
        soup = BeautifulSoup(html_content, "html.parser")
        data = {}
        
        # Buscar tabla con datos del caso
        table = soup.find("table")
        if table:
            rows = table.find_all("tr")
            for row in rows:
                cells = row.find_all(["td", "th"])
                if len(cells) >= 2:
                    key = cells[0].get_text(strip=True).lower()
                    value = cells[1].get_text(strip=True)
                    
                    # Mapear campos de la tabla
                    if "radicado" in key:
                        data["radicado"] = value
                    elif "fecha" in key and "remisi" in key:
                        data["fechaRecepcion"] = self.parse_spanish_date(value)
                    elif "fecha" in key and "vencimiento" in key:
                        data["fechaVencimiento"] = self.parse_spanish_date(value)
                    elif "nombre" in key and "peticionario" in key:
                        data["peticionarioNombre"] = value
                    elif "correo" in key and "peticionario" in key:
                        data["peticionarioCorreo"] = value
                    elif "detalle" in key and "solicitud" in key:
                        data["detalleSolicitud"] = value
                    elif "tipo" in key and "tramite" in key:
                        data["tipoTramite"] = value.lower()
        
        return data

    def extract_radicado(self, text: str) -> str:
        """Extraer radicado desde texto plano"""
        # Buscar patrón "Radicado No." seguido del número
        match = re.search(r'Radicado\s+No\.?\s*[:\-]?\s*([A-Z0-9\-]+)', text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        # Buscar patrón de radicado (formato común: YYYYMMDD-NNNN o similar)
        match = re.search(r'\b(\d{8}-\d{4})\b', text)
        if match:
            return match.group(1)
        
        return None

    def parse_spanish_date(self, date_str: str) -> datetime:
        """Parsear fechas en español (ej: '11 de diciembre de 2025')"""
        if not date_str:
            return None
        
        # Mapeo de meses en español
        meses = {
            'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
            'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
            'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
        }
        
        try:
            # Patrón: "DD de MES de YYYY"
            match = re.search(r'(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})', date_str, re.IGNORECASE)
            if match:
                day = int(match.group(1))
                month_name = match.group(2).lower()
                year = int(match.group(3))
                month = meses.get(month_name)
                
                if month:
                    return datetime(year, month, day)
            
            # Intentar parsear formato ISO
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except Exception:
            return None


ingestion_service = IngestionService()