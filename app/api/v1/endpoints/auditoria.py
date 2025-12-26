from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime

from app.api.deps import get_db, get_current_user_dep
from app.schemas.auditoria import AuditoriaResponse
from app.models.models import AuditoriaEvento
from app.schemas.catalogo import TipoAccionResponse

router = APIRouter()


@router.get("/", response_model=List[AuditoriaResponse])
async def list_auditoria(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    usuario_id: Optional[int] = None,
    caso_id: Optional[uuid.UUID] = None,
    tipo_accion_id: Optional[int] = None,
    fecha_desde: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_dep)
):
    """Listar registros de auditoría con filtros"""
    query = db.query(AuditoriaEvento)

    if usuario_id:
        query = query.filter(AuditoriaEvento.usuarioId == usuario_id)
    if caso_id:
        query = query.filter(AuditoriaEvento.casoId == caso_id)
    if tipo_accion_id:
        query = query.filter(AuditoriaEvento.tipoAccionId == tipo_accion_id)
    if fecha_desde:
        query = query.filter(AuditoriaEvento.fechaEvento >= fecha_desde)

    auditoria = query.order_by(AuditoriaEvento.fechaEvento.desc()).offset(skip).limit(limit).all()
    return auditoria


@router.get("/caso/{caso_id}", response_model=List[AuditoriaResponse])
async def get_auditoria_caso(
    caso_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_dep)
):
    """Obtener auditoría de un caso específico"""
    auditoria = db.query(AuditoriaEvento).filter(AuditoriaEvento.casoId == caso_id).order_by(AuditoriaEvento.fechaEvento.desc()).all()
    return auditoria


@router.get("/usuario/{usuario_id}", response_model=List[AuditoriaResponse])
async def get_auditoria_usuario(
    usuario_id: int,
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_dep)
):
    """Obtener últimas acciones de un usuario"""
    auditoria = db.query(AuditoriaEvento).filter(
        AuditoriaEvento.usuarioId == usuario_id
    ).order_by(AuditoriaEvento.fechaEvento.desc()).limit(limit).all()
    return auditoria
