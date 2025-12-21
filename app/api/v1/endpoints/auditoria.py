from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.api.deps import get_db, get_current_user_dep
from app.schemas.auditoria import AuditoriaResponse, AuditoriaFilter
from app.schemas.common import PaginatedResponse
from app.services.auditoria_service import auditoria_service

router = APIRouter()


@router.get("/", response_model=PaginatedResponse)
async def list_auditoria(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    usuario_id: Optional[int] = None,
    caso_id: Optional[int] = None,
    accion: Optional[str] = None,
    entidad: Optional[str] = None,
    fecha_desde: Optional[datetime] = None,
    fecha_hasta: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_dep)
):
    """Listar registros de auditoría con filtros"""
    filters = AuditoriaFilter(
        usuario_id=usuario_id,
        caso_id=caso_id,
        accion=accion,
        entidad=entidad,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta
    )

    skip = (page - 1) * page_size
    auditoria = auditoria_service.get_auditoria(db, skip=skip, limit=page_size, filters=filters)

    # Contar total (simplificado)
    total = len(auditoria)

    return PaginatedResponse(
        items=[AuditoriaResponse.model_validate(a) for a in auditoria],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/caso/{caso_id}", response_model=List[AuditoriaResponse])
async def get_auditoria_caso(
    caso_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_dep)
):
    """Obtener auditoría de un caso específico"""
    auditoria = auditoria_service.get_cambios_caso(db, caso_id)
    return [AuditoriaResponse.model_validate(a) for a in auditoria]


@router.get("/usuario/{usuario_id}", response_model=List[AuditoriaResponse])
async def get_auditoria_usuario(
    usuario_id: int,
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_dep)
):
    """Obtener últimas acciones de un usuario"""
    auditoria = auditoria_service.get_acciones_usuario(db, usuario_id, limit)
    return [AuditoriaResponse.model_validate(a) for a in auditoria]
