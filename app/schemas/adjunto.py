from pydantic import BaseModel, UUID4
from typing import Optional
from datetime import datetime
from app.schemas.catalogo import TipoAdjuntoResponse

# ==========================================
# Esquemas para Adjuntos
# ==========================================

class AdjuntoBase(BaseModel):
    tipoAdjuntoId: int
    subTipo: Optional[str] = None
    nombreArchivo: str
    mimeType: str
    tamanioBytes: Optional[int] = None
    rutaStorage: str
    
    # Campo opcional si viene de correo
    messageIdOrigen: Optional[str] = None
    version: Optional[int] = 1

class AdjuntoCreate(AdjuntoBase):
    casoId: UUID4

class AdjuntoResponse(AdjuntoBase):
    id: UUID4
    casoId: UUID4
    createdAt: datetime
    
    tipo_adjunto: Optional[TipoAdjuntoResponse] = None
    
    class Config:
        from_attributes = True
