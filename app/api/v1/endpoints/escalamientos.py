from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from app.api.deps import get_db, get_current_user_dep, get_client_info
from app.schemas.escalamiento import EscalamientoCreate, EscalamientoResponse
from app.models.models import Escalamiento, Caso
# from app.services.auditoria_service import auditoria_service
# from app.services.email_service import email_service

router = APIRouter()


@router.get("/", response_model=List[EscalamientoResponse])
async def list_escalamientos(
    skip: int = 0,
    limit: int = 100,
    caso_id: Optional[uuid.UUID] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_dep)
):
    """Listar escalamientos"""
    query = db.query(Escalamiento)
    if caso_id:
        query = query.filter(Escalamiento.casoId == caso_id)

    escalamientos = query.order_by(Escalamiento.fechaEscalamiento.desc()).offset(skip).limit(limit).all()
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
    caso = db.query(Caso).filter(Caso.id == escalamiento.casoId).first()
    if not caso:
        raise HTTPException(status_code=404, detail="Caso no encontrado")

    db_escalamiento = Escalamiento(
        casoId=escalamiento.casoId,
        deUsuarioId=current_user.id,
        aUsuarioId=escalamiento.aUsuarioId,
        observacion=escalamiento.observacion
    )
    db.add(db_escalamiento)
    
    # Actualizar responsable del caso
    caso.responsableId = escalamiento.aUsuarioId
    # TODO: Actualizar estado del caso si es necesario (ej: buscando ID de estado 'Escalado')
    
    db.commit()
    db.refresh(db_escalamiento)

    # TODO: Enviar notificación y auditoría
    
    return db_escalamiento
