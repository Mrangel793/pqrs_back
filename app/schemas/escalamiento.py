from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class EscalamientoBase(BaseModel):
    """Schema base de escalamiento"""
    caso_id: int
    nivel: int
    motivo: str
    escalado_a: str


class EscalamientoCreate(EscalamientoBase):
    """Schema para crear escalamiento"""
    pass


class EscalamientoUpdate(BaseModel):
    """Schema para actualizar escalamiento"""
    estado: Optional[str] = None
    resolucion: Optional[str] = None


class EscalamientoResponse(EscalamientoBase):
    """Schema de respuesta de escalamiento"""
    id: int
    fecha_escalamiento: datetime
    estado: str
    resolucion: Optional[str] = None
    fecha_resolucion: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
