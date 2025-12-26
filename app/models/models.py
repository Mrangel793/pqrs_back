from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER, DATETIME2, BIT
from datetime import datetime
import uuid

from app.database import Base

# =============================================
# TABLAS DE CATÁLOGOS
# =============================================

class EstadoCaso(Base):
    __tablename__ = "tab_estadocaso"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(30), unique=True, nullable=False)
    descripcion = Column(String(100), nullable=False)
    activo = Column(Boolean, default=True, nullable=False)

    # Relaciones
    casos = relationship("Caso", back_populates="estado_caso")


class Semaforo(Base):
    __tablename__ = "tab_semaforo"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(20), unique=True, nullable=False)
    descripcion = Column(String(100))
    colorHex = Column(String(7), nullable=False)
    diasMin = Column(Integer, nullable=False)
    diasMax = Column(Integer, nullable=True)
    orden = Column(Integer, default=0, nullable=False)

    # Relaciones
    casos = relationship("Caso", back_populates="semaforo")


class TipoPDF(Base):
    __tablename__ = "tab_tipopdf"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(30), unique=True, nullable=False)
    descripcion = Column(String(100), nullable=False)
    activo = Column(Boolean, default=True, nullable=False)

    # Relaciones
    casos = relationship("Caso", back_populates="tipo_pdf")


class EstadoEnvio(Base):
    __tablename__ = "tab_estadoenvio"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(20), unique=True, nullable=False)
    descripcion = Column(String(100), nullable=False)

    # Relaciones
    casos = relationship("Caso", back_populates="correo_envio_estado")


class TipoAdjunto(Base):
    __tablename__ = "tab_tipoadjunto"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(30), unique=True, nullable=False)
    descripcion = Column(String(100), nullable=False)

    # Relaciones
    adjuntos = relationship("Adjunto", back_populates="tipo_adjunto")


class TipoAccion(Base):
    __tablename__ = "tab_tipoaccion"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), unique=True, nullable=False)
    descripcion = Column(String(150), nullable=False)

    # Relaciones
    auditorias = relationship("AuditoriaEvento", back_populates="tipo_accion")


# =============================================
# TABLAS PRINCIPALES
# =============================================

class Usuario(Base):
    __tablename__ = "tab_usuario"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    correo = Column(String(150), unique=True, index=True, nullable=False)
    passwordHash = Column(String(255), nullable=True)
    activo = Column(Boolean, default=True, nullable=False)
    createdAt = Column(DATETIME2, default=datetime.now, nullable=False)
    updatedAt = Column(DATETIME2, default=datetime.now, onupdate=datetime.now, nullable=False)

    # Relaciones
    casos_asignados = relationship("Caso", back_populates="responsable")
    auditorias = relationship("AuditoriaEvento", back_populates="usuario")
    escalamientos_origen = relationship("Escalamiento", foreign_keys="[Escalamiento.deUsuarioId]", back_populates="de_usuario")
    escalamientos_destino = relationship("Escalamiento", foreign_keys="[Escalamiento.aUsuarioId]", back_populates="a_usuario")
    sesiones = relationship("Sesion", back_populates="usuario")
    log_ingestas = relationship("LogIngesta", back_populates="ejecutado_por_usuario")


class Caso(Base):
    __tablename__ = "tab_caso"

    id = Column(UNIQUEIDENTIFIER(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Identificación
    radicado = Column(String(50), unique=True, nullable=False, index=True)
    
    # Fechas
    fechaRecepcion = Column(DATETIME2, nullable=False)
    fechaEscalamientoTecnologia = Column(DATETIME2, nullable=True)
    fechaVencimiento = Column(DATETIME2, nullable=False, index=True)
    
    # Peticionario
    peticionarioNombre = Column(String(200), nullable=False)
    peticionarioCorreo = Column(String(150), nullable=False)
    
    # Solicitud
    detalleSolicitud = Column(Text, nullable=False) # NVARCHAR(MAX)
    tipoTramite = Column(String(100), nullable=False)
    
    # Estado y asignación
    estadoCasoId = Column(Integer, ForeignKey("tab_estadocaso.id"), nullable=False)
    semaforoId = Column(Integer, ForeignKey("tab_semaforo.id"), nullable=False)
    responsableId = Column(Integer, ForeignKey("tab_usuario.id"), nullable=True)
    
    # Destinatario de respuesta
    destinatarioCorreo = Column(String(150), nullable=False)
    
    # Respuesta
    respuestaContenido = Column(Text, nullable=True)
    respuestaTextoAdicional = Column(Text, nullable=True)
    tipoPDFId = Column(Integer, ForeignKey("tab_tipopdf.id"), nullable=True)
    
    # Datos del hilo de correo
    correoHiloId = Column(String(255), nullable=False)
    correoMensajeSalidaId = Column(String(255), nullable=True)
    correoEnvioEstadoId = Column(Integer, ForeignKey("tab_estadoenvio.id"), nullable=False, default=1)
    correoEnvioFecha = Column(DATETIME2, nullable=True)
    
    # Auditoría
    createdAt = Column(DATETIME2, default=datetime.now, nullable=False)
    updatedAt = Column(DATETIME2, default=datetime.now, onupdate=datetime.now, nullable=False)

    # Relaciones
    estado_caso = relationship("EstadoCaso", back_populates="casos")
    semaforo = relationship("Semaforo", back_populates="casos")
    responsable = relationship("Usuario", back_populates="casos_asignados")
    tipo_pdf = relationship("TipoPDF", back_populates="casos")
    correo_envio_estado = relationship("EstadoEnvio", back_populates="casos")
    
    identificadores = relationship("CasoIdentificador", back_populates="caso", cascade="all, delete-orphan")
    escalamientos = relationship("Escalamiento", back_populates="caso", cascade="all, delete-orphan")
    adjuntos = relationship("Adjunto", back_populates="caso", cascade="all, delete-orphan")
    fuentes_correo = relationship("FuenteCorreo", back_populates="caso", cascade="all, delete-orphan")
    auditorias = relationship("AuditoriaEvento", back_populates="caso", cascade="all, delete-orphan")


class CasoIdentificador(Base):
    __tablename__ = "tab_casoidentificador"

    id = Column(Integer, primary_key=True, index=True)
    casoId = Column(UNIQUEIDENTIFIER(as_uuid=True), ForeignKey("tab_caso.id"), nullable=False)
    clave = Column(String(50), nullable=False)
    valor = Column(String(255), nullable=False)

    # Relaciones
    caso = relationship("Caso", back_populates="identificadores")


class Escalamiento(Base):
    __tablename__ = "tab_escalamiento"

    id = Column(Integer, primary_key=True, index=True)
    casoId = Column(UNIQUEIDENTIFIER(as_uuid=True), ForeignKey("tab_caso.id"), nullable=False)
    deUsuarioId = Column(Integer, ForeignKey("tab_usuario.id"), nullable=False)
    aUsuarioId = Column(Integer, ForeignKey("tab_usuario.id"), nullable=False)
    fechaEscalamiento = Column(DATETIME2, default=datetime.now, nullable=False)
    observacion = Column(Text, nullable=False)

    # Relaciones
    caso = relationship("Caso", back_populates="escalamientos")
    de_usuario = relationship("Usuario", foreign_keys=[deUsuarioId], back_populates="escalamientos_origen")
    a_usuario = relationship("Usuario", foreign_keys=[aUsuarioId], back_populates="escalamientos_destino")


class Adjunto(Base):
    __tablename__ = "tab_adjunto"

    id = Column(UNIQUEIDENTIFIER(as_uuid=True), primary_key=True, default=uuid.uuid4)
    casoId = Column(UNIQUEIDENTIFIER(as_uuid=True), ForeignKey("tab_caso.id"), nullable=False)
    tipoAdjuntoId = Column(Integer, ForeignKey("tab_tipoadjunto.id"), nullable=False)
    subTipo = Column(String(30), nullable=True)
    version = Column(Integer, default=1, nullable=True)
    messageIdOrigen = Column(String(255), nullable=True)
    nombreArchivo = Column(String(255), nullable=False)
    mimeType = Column(String(100), nullable=False)
    tamanioBytes = Column(BigInteger, nullable=True)
    rutaStorage = Column(String(500), nullable=False)
    createdAt = Column(DATETIME2, default=datetime.now, nullable=False)

    # Relaciones
    caso = relationship("Caso", back_populates="adjuntos")
    tipo_adjunto = relationship("TipoAdjunto", back_populates="adjuntos")


class FuenteCorreo(Base):
    __tablename__ = "tab_fuentecorreo"

    id = Column(UNIQUEIDENTIFIER(as_uuid=True), primary_key=True, default=uuid.uuid4)
    casoId = Column(UNIQUEIDENTIFIER(as_uuid=True), ForeignKey("tab_caso.id"), nullable=False)
    direccion = Column(String(3), nullable=False) # IN, OUT
    messageId = Column(String(255), unique=True, nullable=False)
    conversationId = Column(String(255), nullable=False)
    inReplyTo = Column(String(255), nullable=True)
    referencias = Column(Text, nullable=True)
    asunto = Column(String(500), nullable=True)
    remitente = Column(String(200), nullable=False)
    destinatariosTo = Column(String(1000), nullable=True)
    destinatariosCc = Column(String(1000), nullable=True)
    fechaCorreo = Column(DATETIME2, nullable=False)
    snippet = Column(String(1000), nullable=True)
    cuerpoHtml = Column(Text, nullable=True)
    createdAt = Column(DATETIME2, default=datetime.now, nullable=False)

    # Relaciones
    caso = relationship("Caso", back_populates="fuentes_correo")


class AuditoriaEvento(Base):
    __tablename__ = "tab_auditoriaevento"

    id = Column(BigInteger, primary_key=True, index=True)
    casoId = Column(UNIQUEIDENTIFIER(as_uuid=True), ForeignKey("tab_caso.id"), nullable=True)
    usuarioId = Column(Integer, ForeignKey("tab_usuario.id"), nullable=True)
    tipoAccionId = Column(Integer, ForeignKey("tab_tipoaccion.id"), nullable=False)
    detalleJson = Column(Text, nullable=True)
    ipOrigen = Column(String(45), nullable=True)
    fechaEvento = Column(DATETIME2, default=datetime.now, nullable=False)

    # Relaciones
    caso = relationship("Caso", back_populates="auditorias")
    usuario = relationship("Usuario", back_populates="auditorias")
    tipo_accion = relationship("TipoAccion", back_populates="auditorias")


class Configuracion(Base):
    __tablename__ = "tab_configuracion"

    id = Column(Integer, primary_key=True, index=True)
    clave = Column(String(100), unique=True, nullable=False)
    valor = Column(Text, nullable=False)
    tipoDato = Column(String(20), default='STRING', nullable=False)
    descripcion = Column(String(255), nullable=True)
    editable = Column(Boolean, default=True, nullable=False)
    updatedAt = Column(DATETIME2, default=datetime.now, onupdate=datetime.now, nullable=False)
    updatedBy = Column(Integer, ForeignKey("tab_usuario.id"), nullable=True)

    # Relaciones
    # usuario_modificador = relationship("Usuario") # Opcional


class LogIngesta(Base):
    __tablename__ = "tab_logingesta"

    id = Column(BigInteger, primary_key=True, index=True)
    fechaInicio = Column(DATETIME2, default=datetime.now, nullable=False)
    fechaFin = Column(DATETIME2, nullable=True)
    tipoEjecucion = Column(String(20), default='AUTOMATICA', nullable=False)
    backfillDesde = Column(DATETIME2, nullable=True)
    backfillHasta = Column(DATETIME2, nullable=True)
    correosLeidos = Column(Integer, default=0, nullable=False)
    casosCreados = Column(Integer, default=0, nullable=False)
    casosActualizados = Column(Integer, default=0, nullable=False)
    casosExistentes = Column(Integer, default=0, nullable=False)
    errores = Column(Integer, default=0, nullable=False)
    estado = Column(String(20), default='EN_PROCESO', nullable=False)
    detalleErrores = Column(Text, nullable=True)
    ejecutadoPor = Column(Integer, ForeignKey("tab_usuario.id"), nullable=True)

    # Relaciones
    ejecutado_por_usuario = relationship("Usuario", back_populates="log_ingestas")


class Sesion(Base):
    __tablename__ = "tab_sesion"

    id = Column(UNIQUEIDENTIFIER(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuarioId = Column(Integer, ForeignKey("tab_usuario.id"), nullable=False)
    token = Column(String(500), nullable=False, index=True)
    fechaCreacion = Column(DATETIME2, default=datetime.now, nullable=False)
    fechaExpiracion = Column(DATETIME2, nullable=False, index=True)
    activa = Column(Boolean, default=True, nullable=False)
    ipOrigen = Column(String(45), nullable=True)
    userAgent = Column(String(500), nullable=True)

    # Relaciones
    usuario = relationship("Usuario", back_populates="sesiones")
