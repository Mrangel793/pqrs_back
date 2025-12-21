from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import json
from datetime import datetime

from app.models.models import Auditoria
from app.schemas.auditoria import AuditoriaCreate, AuditoriaFilter


class AuditoriaService:
    """Servicio para auditoría y registro de acciones"""

    def registrar_accion(
        self,
        db: Session,
        accion: str,
        entidad: str,
        entidad_id: Optional[int] = None,
        usuario_id: Optional[int] = None,
        caso_id: Optional[int] = None,
        detalles: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Auditoria:
        """Registrar acción de auditoría"""
        auditoria = Auditoria(
            usuario_id=usuario_id,
            caso_id=caso_id,
            accion=accion,
            entidad=entidad,
            entidad_id=entidad_id,
            detalles=json.dumps(detalles) if detalles else None,
            ip_address=ip_address,
            user_agent=user_agent
        )

        db.add(auditoria)
        db.commit()
        db.refresh(auditoria)
        return auditoria

    def get_auditoria(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[AuditoriaFilter] = None
    ):
        """Obtener registros de auditoría con filtros"""
        query = db.query(Auditoria)

        if filters:
            if filters.usuario_id:
                query = query.filter(Auditoria.usuario_id == filters.usuario_id)
            if filters.caso_id:
                query = query.filter(Auditoria.caso_id == filters.caso_id)
            if filters.accion:
                query = query.filter(Auditoria.accion == filters.accion)
            if filters.entidad:
                query = query.filter(Auditoria.entidad == filters.entidad)
            if filters.fecha_desde:
                query = query.filter(Auditoria.created_at >= filters.fecha_desde)
            if filters.fecha_hasta:
                query = query.filter(Auditoria.created_at <= filters.fecha_hasta)

        return query.order_by(Auditoria.created_at.desc()).offset(skip).limit(limit).all()

    def get_cambios_caso(self, db: Session, caso_id: int):
        """Obtener todos los cambios de un caso"""
        return db.query(Auditoria).filter(Auditoria.caso_id == caso_id).order_by(Auditoria.created_at).all()

    def get_acciones_usuario(self, db: Session, usuario_id: int, limit: int = 50):
        """Obtener últimas acciones de un usuario"""
        return db.query(Auditoria).filter(
            Auditoria.usuario_id == usuario_id
        ).order_by(Auditoria.created_at.desc()).limit(limit).all()


auditoria_service = AuditoriaService()
