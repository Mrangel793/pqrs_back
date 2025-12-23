from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

# ==========================================
# Esquemas para Sesiones
# ==========================================

class SesionBase(BaseModel):
    """Schema base de sesión"""
    usuarioId: int
    token: str
    fechaExpiracion: datetime
    activa: bool = True
    ipOrigen: Optional[str] = None
    userAgent: Optional[str] = None


class SesionCreate(SesionBase):
    """Schema para crear sesión (uso interno)"""
    pass


class SesionResponse(BaseModel):
    """Schema de respuesta de sesión"""
    id: UUID
    usuarioId: int
    fechaCreacion: datetime
    fechaExpiracion: datetime
    activa: bool
    ipOrigen: Optional[str] = None

    class Config:
        from_attributes = True


class SesionInDB(SesionBase):
    """Schema completo de sesión en DB"""
    id: UUID
    fechaCreacion: datetime

    class Config:
        from_attributes = True
