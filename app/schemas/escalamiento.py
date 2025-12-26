from pydantic import BaseModel, UUID4
from typing import Optional
from datetime import datetime
from app.schemas.usuario import UsuarioResponse

# ==========================================
# Esquemas para Escalamientos
# ==========================================

class EscalamientoBase(BaseModel):
    observacion: str

class EscalamientoCreate(EscalamientoBase):
    casoId: UUID4
    aUsuarioId: int

class EscalamientoResponse(EscalamientoBase):
    id: int
    casoId: UUID4
    deUsuarioId: int
    aUsuarioId: int
    fechaEscalamiento: datetime
    
    # Relaciones
    de_usuario: Optional[UsuarioResponse] = None
    a_usuario: Optional[UsuarioResponse] = None
    
    class Config:
        from_attributes = True
