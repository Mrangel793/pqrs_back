from pydantic import BaseModel
from typing import Optional

# ==========================================
# Esquemas para Catálogos
# ==========================================

class CatalogoBase(BaseModel):
    codigo: str
    descripcion: str

    class Config:
        from_attributes = True

class EstadoCasoResponse(CatalogoBase):
    id: int
    activo: bool

class SemaforoResponse(CatalogoBase):
    id: int
    colorHex: str
    diasMin: int
    diasMax: Optional[int] = None
    orden: int

class TipoPDFResponse(CatalogoBase):
    id: int
    activo: bool

class EstadoEnvioResponse(CatalogoBase):
    id: int

class TipoAdjuntoResponse(CatalogoBase):
    id: int

class TipoAccionResponse(CatalogoBase):
    id: int
