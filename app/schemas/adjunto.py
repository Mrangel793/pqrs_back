from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AdjuntoBase(BaseModel):
    """Schema base de adjunto"""
    nombre_archivo: str
    ruta_archivo: str
    tipo_mime: Optional[str] = None
    tamano: Optional[int] = None


class AdjuntoCreate(AdjuntoBase):
    """Schema para crear adjunto"""
    caso_id: int


class AdjuntoResponse(AdjuntoBase):
    """Schema de respuesta de adjunto"""
    id: int
    caso_id: int
    created_at: datetime

    class Config:
        from_attributes = True
