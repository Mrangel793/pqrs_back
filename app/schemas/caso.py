from pydantic import BaseModel, EmailStr, UUID4, Field
from typing import Optional, List, Any
from datetime import datetime
from app.schemas.catalogo import EstadoCasoResponse, SemaforoResponse, TipoPDFResponse, EstadoEnvioResponse
from app.schemas.usuario import UsuarioResponse

# ==========================================
# Esquemas para Casos
# ==========================================

class CasoIdentificadorBase(BaseModel):
    clave: str
    valor: str

class CasoIdentificadorResponse(CasoIdentificadorBase):
    id: int
    class Config:
        from_attributes = True

class FuenteCorreoResponse(BaseModel):
    id: UUID4
    direccion: str
    fechaCorreo: datetime
    remitente: str
    asunto: Optional[str] = None
    snippet: Optional[str] = None
    class Config:
        from_attributes = True

class CasoBase(BaseModel):
    radicado: str
    fechaRecepcion: datetime
    fechaEscalamientoTecnologia: Optional[datetime] = None
    fechaVencimiento: datetime
    
    peticionarioNombre: str
    peticionarioCorreo: EmailStr
    
    detalleSolicitud: str
    tipoTramite: str
    
    estadoCasoId: int
    semaforoId: int
    responsableId: Optional[int] = None
    
    destinatarioCorreo: EmailStr
    
    respuestaContenido: Optional[str] = None
    respuestaTextoAdicional: Optional[str] = None
    tipoPDFId: Optional[int] = None
    
    correoHiloId: str
    correoMensajeSalidaId: Optional[str] = None
    correoEnvioEstadoId: int = 1
    
class CasoCreate(CasoBase):
    # Identificadores opcionales al crear
    identificadores: Optional[List[CasoIdentificadorBase]] = []

class CasoFilter(BaseModel):
    tipoTramite: Optional[str] = None
    estadoCasoId: Optional[int] = None
    semaforoId: Optional[int] = None
    responsableId: Optional[int] = None
    fechaDesde: Optional[datetime] = None
    fechaHasta: Optional[datetime] = None
    busqueda: Optional[str] = None
    radicado: Optional[str] = None

class CasoUpdate(BaseModel):
    estadoCasoId: Optional[int] = None
    responsableId: Optional[int] = None
    respuestaContenido: Optional[str] = None
    respuestaTextoAdicional: Optional[str] = None
    tipoPDFId: Optional[int] = None
    correoMensajeSalidaId: Optional[str] = None
    correoEnvioEstadoId: Optional[int] = None
    correoEnvioFecha: Optional[datetime] = None

class CasoResponse(CasoBase):
    id: UUID4
    createdAt: datetime
    updatedAt: datetime
    
    # Relaciones expandidas
    estado_caso: Optional[EstadoCasoResponse] = None
    semaforo: Optional[SemaforoResponse] = None
    responsable: Optional[UsuarioResponse] = None
    tipo_pdf: Optional[TipoPDFResponse] = None
    correo_envio_estado: Optional[EstadoEnvioResponse] = None
    
    identificadores: List[CasoIdentificadorResponse] = []
    
    class Config:
        from_attributes = True

class CasoListResponse(BaseModel):
    total: int
    items: List[CasoResponse]
