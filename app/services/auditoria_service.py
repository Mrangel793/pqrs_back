from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
import json
import uuid
from datetime import datetime

from app.models.models import AuditoriaEvento
# from app.schemas.auditoria import AuditoriaFilter # Filter is generic or custom

class AuditoriaService:
    """Servicio para auditoría y registro de acciones"""

    def registrar_accion(
        self,
        db: Session,
        accion: str, # TODO: Mapear 'accion' string a 'tipoAccionId' int
        entidad: str, # No usado directamente en modelo, solo para logica
        entidad_id: Optional[str] = None, # Puede ser int o uuid
        usuario_id: Optional[int] = None,
        caso_id: Optional[uuid.UUID] = None,
        detalles: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditoriaEvento:
        """Registrar acción de auditoría"""
        
        # Mapeo temporal de acciones a IDs (esto debería venir de DB o constante)
        # Asumimos IDs : 1=Login, 2=CrearCaso, 3=ActualizarCaso, 4=EliminarCaso, etc.
        # Por ahora usaremos 1 genérico si no lo tenemos, o mejor, no registramos si no tenemos el ID
        # Necesitamos la tabla `tab_tipoaccion` poblada. 
        # Supongamos:
        # 1: Crear
        # 2: Actualizar
        # 3: Eliminar
        # 4: Login
        # 5: Escalar
        
        tipo_accion_map = {
            "crear": 1,
            "actualizar": 2,
            "eliminar": 3,
            "login": 4,
            "recuperar_pass": 5,
            "crear_escalamiento": 6, # Asumido
            "actualizar_escalamiento": 7
        }
        
        tipo_accion_id = tipo_accion_map.get(accion, 99) # 99=Desconocido o genérico

        auditoria = AuditoriaEvento(
            tipoAccionId=tipo_accion_id,
            usuarioId=usuario_id,
            casoId=caso_id,
            detalleJson=json.dumps(detalles) if detalles else None,
            ipOrigen=ip_address
            # entidad_id no se guarda explícitamente si no es casoId, pero podríamos meterlo en detalles
        )

        db.add(auditoria)
        try:
            db.commit()
            db.refresh(auditoria)
        except Exception as e:
            print(f"Error registrando auditoria: {e}")
            db.rollback()
            return None
            
        return auditoria

    def get_auditoria(self, db: Session, skip: int=0, limit: int=100, filters: Any=None):
        # Implementado en endpoint directamente por simplicidad ahora
        pass

    def get_cambios_caso(self, db: Session, caso_id: uuid.UUID):
        return db.query(AuditoriaEvento).filter(AuditoriaEvento.casoId == caso_id).order_by(AuditoriaEvento.fechaEvento).all()

    def get_acciones_usuario(self, db: Session, usuario_id: int, limit: int = 50):
        return db.query(AuditoriaEvento).filter(
            AuditoriaEvento.usuarioId == usuario_id
        ).order_by(AuditoriaEvento.fechaEvento.desc()).limit(limit).all()


auditoria_service = AuditoriaService()
