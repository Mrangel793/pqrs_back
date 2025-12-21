from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AuditoriaBase(BaseModel):
    """Schema base de auditoría"""
    accion: str
    entidad: str
    entidad_id: Optional[int] = None
    detalles: Optional[str] = None


class AuditoriaCreate(AuditoriaBase):
    """Schema para crear auditoría"""
    usuario_id: Optional[int] = None
    caso_id: Optional[int] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class AuditoriaResponse(AuditoriaBase):
    """Schema de respuesta de auditoría"""
    id: int
    usuario_id: Optional[int] = None
    caso_id: Optional[int] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AuditoriaFilter(BaseModel):
    """Filtros para búsqueda de auditoría"""
    usuario_id: Optional[int] = None
    caso_id: Optional[int] = None
    accion: Optional[str] = None
    entidad: Optional[str] = None
    fecha_desde: Optional[datetime] = None
    fecha_hasta: Optional[datetime] = None
