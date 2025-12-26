from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas.usuario import UsuarioResponse

# ==========================================
# Esquemas para Configuración
# ==========================================

class ConfiguracionBase(BaseModel):
    clave: str
    valor: str
    tipoDato: str = "STRING"
    descripcion: Optional[str] = None
    editable: bool = True

class ConfiguracionCreate(ConfiguracionBase):
    pass

class ConfiguracionUpdate(BaseModel):
    valor: Optional[str] = None
    descripcion: Optional[str] = None
    # clave y tipoDato usualmente no se cambian libremente

class ConfiguracionResponse(ConfiguracionBase):
    id: int
    updatedAt: datetime
    updatedBy: Optional[int] = None
    
    # Relaciones - Nota: en modelo dejamos usuario_modificador comentado, si se descomenta se agrega aquí
    # usuario_modificador: Optional[UsuarioResponse] = None

    class Config:
        from_attributes = True
