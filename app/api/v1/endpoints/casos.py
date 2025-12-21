from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.api.deps import get_db, get_current_user_dep, get_client_info
from app.schemas.caso import CasoCreate, CasoResponse, CasoUpdate, CasoDetalle, CasoFilter
from app.schemas.common import PaginatedResponse
from app.services import caso_service
from app.services.auditoria_service import auditoria_service

router = APIRouter()


@router.get("/", response_model=PaginatedResponse)
async def list_casos(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    tipo: Optional[str] = None,
    estado: Optional[str] = None,
    prioridad: Optional[str] = None,
    busqueda: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_dep)
):
    """Listar casos con filtros y paginación"""
    filters = CasoFilter(
        tipo=tipo,
        estado=estado,
        prioridad=prioridad,
        busqueda=busqueda
    )

    skip = (page - 1) * page_size
    casos = caso_service.get_casos(db, skip=skip, limit=page_size, filters=filters)
    total = caso_service.count_casos(db, filters=filters)

    return PaginatedResponse(
        items=[CasoResponse.model_validate(c) for c in casos],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/{caso_id}", response_model=CasoDetalle)
async def get_caso(
    caso_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_dep)
):
    """Obtener caso por ID con detalles"""
    caso = caso_service.get_caso(db, caso_id)
    return caso


@router.post("/", response_model=CasoResponse, status_code=201)
async def create_caso(
    caso: CasoCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_dep),
    client_info: dict = Depends(get_client_info)
):
    """Crear nuevo caso"""
    db_caso = caso_service.create_caso(db, caso)

    # Registrar auditoría
    auditoria_service.registrar_accion(
        db=db,
        accion="crear",
        entidad="caso",
        entidad_id=db_caso.id,
        usuario_id=current_user.get("id"),
        caso_id=db_caso.id,
        detalles={"numero_caso": db_caso.numero_caso, "tipo": db_caso.tipo},
        **client_info
    )

    return db_caso


@router.put("/{caso_id}", response_model=CasoResponse)
async def update_caso(
    caso_id: int,
    caso_update: CasoUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_dep),
    client_info: dict = Depends(get_client_info)
):
    """Actualizar caso"""
    db_caso = caso_service.update_caso(db, caso_id, caso_update)

    # Registrar auditoría
    auditoria_service.registrar_accion(
        db=db,
        accion="actualizar",
        entidad="caso",
        entidad_id=caso_id,
        usuario_id=current_user.get("id"),
        caso_id=caso_id,
        detalles=caso_update.model_dump(exclude_unset=True),
        **client_info
    )

    return db_caso


@router.delete("/{caso_id}", status_code=204)
async def delete_caso(
    caso_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_dep),
    client_info: dict = Depends(get_client_info)
):
    """Eliminar caso"""
    caso_service.delete_caso(db, caso_id)

    # Registrar auditoría
    auditoria_service.registrar_accion(
        db=db,
        accion="eliminar",
        entidad="caso",
        entidad_id=caso_id,
        usuario_id=current_user.get("id"),
        **client_info
    )

    return None
