from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db, get_current_user_dep, get_client_info
from app.schemas.escalamiento import EscalamientoCreate, EscalamientoResponse, EscalamientoUpdate
from app.models.models import Escalamiento, Caso
from app.services.auditoria_service import auditoria_service
from app.services.email_service import email_service

router = APIRouter()


@router.get("/", response_model=List[EscalamientoResponse])
async def list_escalamientos(
    skip: int = 0,
    limit: int = 100,
    caso_id: int = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_dep)
):
    """Listar escalamientos"""
    query = db.query(Escalamiento)
    if caso_id:
        query = query.filter(Escalamiento.caso_id == caso_id)

    escalamientos = query.offset(skip).limit(limit).all()
    return escalamientos


@router.get("/{escalamiento_id}", response_model=EscalamientoResponse)
async def get_escalamiento(
    escalamiento_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_dep)
):
    """Obtener escalamiento por ID"""
    escalamiento = db.query(Escalamiento).filter(Escalamiento.id == escalamiento_id).first()
    if not escalamiento:
        raise HTTPException(status_code=404, detail="Escalamiento no encontrado")
    return escalamiento


@router.post("/", response_model=EscalamientoResponse, status_code=status.HTTP_201_CREATED)
async def create_escalamiento(
    escalamiento: EscalamientoCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_dep),
    client_info: dict = Depends(get_client_info)
):
    """Crear nuevo escalamiento"""
    # Verificar que el caso existe
    caso = db.query(Caso).filter(Caso.id == escalamiento.caso_id).first()
    if not caso:
        raise HTTPException(status_code=404, detail="Caso no encontrado")

    db_escalamiento = Escalamiento(**escalamiento.model_dump())
    db.add(db_escalamiento)

    # Actualizar estado del caso
    caso.estado = "escalado"

    db.commit()
    db.refresh(db_escalamiento)

    # Enviar notificación
    await email_service.send_escalation_notification(
        to=[escalamiento.escalado_a],
        numero_caso=caso.numero_caso,
        nivel=escalamiento.nivel,
        motivo=escalamiento.motivo
    )

    # Registrar auditoría
    auditoria_service.registrar_accion(
        db=db,
        accion="crear_escalamiento",
        entidad="escalamiento",
        entidad_id=db_escalamiento.id,
        usuario_id=current_user.get("id"),
        caso_id=escalamiento.caso_id,
        detalles={"nivel": escalamiento.nivel, "motivo": escalamiento.motivo},
        **client_info
    )

    return db_escalamiento


@router.put("/{escalamiento_id}", response_model=EscalamientoResponse)
async def update_escalamiento(
    escalamiento_id: int,
    escalamiento_update: EscalamientoUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_dep),
    client_info: dict = Depends(get_client_info)
):
    """Actualizar escalamiento"""
    db_escalamiento = db.query(Escalamiento).filter(Escalamiento.id == escalamiento_id).first()
    if not db_escalamiento:
        raise HTTPException(status_code=404, detail="Escalamiento no encontrado")

    update_data = escalamiento_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_escalamiento, field, value)

    db.commit()
    db.refresh(db_escalamiento)

    # Registrar auditoría
    auditoria_service.registrar_accion(
        db=db,
        accion="actualizar_escalamiento",
        entidad="escalamiento",
        entidad_id=escalamiento_id,
        usuario_id=current_user.get("id"),
        caso_id=db_escalamiento.caso_id,
        detalles=update_data,
        **client_info
    )

    return db_escalamiento
