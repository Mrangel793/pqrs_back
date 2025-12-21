from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ConfiguracionBase(BaseModel):
    """Schema base de configuración"""
    clave: str
    valor: Optional[str] = None
    descripcion: Optional[str] = None
    tipo: str = "string"


class ConfiguracionCreate(ConfiguracionBase):
    """Schema para crear configuración"""
    pass


class ConfiguracionUpdate(BaseModel):
    """Schema para actualizar configuración"""
    valor: Optional[str] = None
    descripcion: Optional[str] = None


class ConfiguracionResponse(ConfiguracionBase):
    """Schema de respuesta de configuración"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
