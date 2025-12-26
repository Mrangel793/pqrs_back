from pydantic import BaseModel, UUID4
from typing import Optional
from datetime import datetime
from app.schemas.catalogo import TipoAccionResponse
from app.schemas.usuario import UsuarioResponse

# ==========================================
# Esquemas para Auditoría
# ==========================================

class AuditoriaBase(BaseModel):
    tipoAccionId: int
    detalleJson: Optional[str] = None
    ipOrigen: Optional[str] = None

class AuditoriaCreate(AuditoriaBase):
    casoId: Optional[UUID4] = None
    usuarioId: Optional[int] = None

class AuditoriaResponse(AuditoriaBase):
    id: int
    casoId: Optional[UUID4] = None
    usuarioId: Optional[int] = None
    fechaEvento: datetime
    
    # Relaciones
    tipo_accion: Optional[TipoAccionResponse] = None
    usuario: Optional[UsuarioResponse] = None
    
    class Config:
        from_attributes = True
