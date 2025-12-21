from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class CasoBase(BaseModel):
    """Schema base de caso"""
    numero_caso: str
    tipo: str
    asunto: str
    descripcion: Optional[str] = None
    prioridad: str = "media"


class CasoCreate(BaseModel):
    """Schema para crear caso"""
    tipo: str
    asunto: str
    descripcion: Optional[str] = None
    prioridad: str = "media"
    email_origen: Optional[str] = None
    usuario_asignado_id: Optional[int] = None


class CasoUpdate(BaseModel):
    """Schema para actualizar caso"""
    asunto: Optional[str] = None
    descripcion: Optional[str] = None
    estado: Optional[str] = None
    prioridad: Optional[str] = None
    usuario_asignado_id: Optional[int] = None
    respuesta: Optional[str] = None


class CasoResponse(CasoBase):
    """Schema de respuesta de caso"""
    id: int
    estado: str
    fecha_recepcion: datetime
    fecha_vencimiento: Optional[datetime] = None
    fecha_cierre: Optional[datetime] = None
    usuario_asignado_id: Optional[int] = None
    email_origen: Optional[str] = None
    respuesta: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CasoDetalle(CasoResponse):
    """Schema detallado de caso con relaciones"""
    escalamientos: List = []
    adjuntos: List = []

    class Config:
        from_attributes = True


class CasoFilter(BaseModel):
    """Filtros para búsqueda de casos"""
    tipo: Optional[str] = None
    estado: Optional[str] = None
    prioridad: Optional[str] = None
    usuario_asignado_id: Optional[int] = None
    fecha_desde: Optional[datetime] = None
    fecha_hasta: Optional[datetime] = None
    busqueda: Optional[str] = None
