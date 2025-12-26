from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db, get_admin_user
from app.schemas.configuracion import ConfiguracionCreate, ConfiguracionResponse, ConfiguracionUpdate
from app.models.models import Configuracion

router = APIRouter()


@router.get("/", response_model=List[ConfiguracionResponse])
async def list_configuraciones(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """Listar configuraciones"""
    configs = db.query(Configuracion).order_by(Configuracion.clave).offset(skip).limit(limit).all()
    return configs


@router.get("/{clave}", response_model=ConfiguracionResponse)
async def get_configuracion(
    clave: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """Obtener configuración por clave"""
    config = db.query(Configuracion).filter(Configuracion.clave == clave).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuración no encontrada")
    return config


@router.post("/", response_model=ConfiguracionResponse, status_code=status.HTTP_201_CREATED)
async def create_configuracion(
    config: ConfiguracionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """Crear nueva configuración"""
    existing = db.query(Configuracion).filter(Configuracion.clave == config.clave).first()
    if existing:
        raise HTTPException(status_code=400, detail="La configuración ya existe")

    db_config = Configuracion(**config.model_dump())
    # Opcional: setear updatedBy en creación si se desea
    # db_config.updatedBy = current_user.id 
    
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config


@router.put("/{clave}", response_model=ConfiguracionResponse)
async def update_configuracion(
    clave: str,
    config_update: ConfiguracionUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """Actualizar configuración"""
    db_config = db.query(Configuracion).filter(Configuracion.clave == clave).first()
    if not db_config:
        raise HTTPException(status_code=404, detail="Configuración no encontrada")

    update_data = config_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_config, field, value)

    # Actualizar auditoría
    db_config.updatedBy = current_user.id

    db.commit()
    db.refresh(db_config)
    return db_config


@router.delete("/{clave}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_configuracion(
    clave: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """Eliminar configuración"""
    db_config = db.query(Configuracion).filter(Configuracion.clave == clave).first()
    if not db_config:
        raise HTTPException(status_code=404, detail="Configuración no encontrada")

    db.delete(db_config)
    db.commit()
    return None
