from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    nombre_completo = Column(String(255))
    rol = Column(String(50), nullable=False)  # admin, gestor, consulta
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    casos_asignados = relationship("Caso", back_populates="usuario_asignado")
    auditorias = relationship("Auditoria", back_populates="usuario")


class Caso(Base):
    __tablename__ = "casos"

    id = Column(Integer, primary_key=True, index=True)
    numero_caso = Column(String(50), unique=True, index=True, nullable=False)
    tipo = Column(String(50), nullable=False)  # peticion, queja, reclamo
    asunto = Column(String(500), nullable=False)
    descripcion = Column(Text)
    estado = Column(String(50), nullable=False)  # nuevo, en_proceso, escalado, cerrado
    prioridad = Column(String(50), default="media")  # baja, media, alta, critica
    fecha_recepcion = Column(DateTime, default=datetime.utcnow)
    fecha_vencimiento = Column(DateTime)
    fecha_cierre = Column(DateTime)
    usuario_asignado_id = Column(Integer, ForeignKey("usuarios.id"))
    email_origen = Column(String(255))
    respuesta = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    usuario_asignado = relationship("Usuario", back_populates="casos_asignados")
    escalamientos = relationship("Escalamiento", back_populates="caso")
    adjuntos = relationship("Adjunto", back_populates="caso")
    auditorias = relationship("Auditoria", back_populates="caso")


class Escalamiento(Base):
    __tablename__ = "escalamientos"

    id = Column(Integer, primary_key=True, index=True)
    caso_id = Column(Integer, ForeignKey("casos.id"), nullable=False)
    nivel = Column(Integer, nullable=False)  # 1, 2, 3
    motivo = Column(Text, nullable=False)
    fecha_escalamiento = Column(DateTime, default=datetime.utcnow)
    escalado_a = Column(String(255))  # email o departamento
    estado = Column(String(50), default="pendiente")  # pendiente, resuelto
    resolucion = Column(Text)
    fecha_resolucion = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    caso = relationship("Caso", back_populates="escalamientos")


class Adjunto(Base):
    __tablename__ = "adjuntos"

    id = Column(Integer, primary_key=True, index=True)
    caso_id = Column(Integer, ForeignKey("casos.id"), nullable=False)
    nombre_archivo = Column(String(255), nullable=False)
    ruta_archivo = Column(String(500), nullable=False)
    tipo_mime = Column(String(100))
    tamano = Column(Integer)  # en bytes
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    caso = relationship("Caso", back_populates="adjuntos")


class Configuracion(Base):
    __tablename__ = "configuracion"

    id = Column(Integer, primary_key=True, index=True)
    clave = Column(String(100), unique=True, nullable=False)
    valor = Column(Text)
    descripcion = Column(String(500))
    tipo = Column(String(50))  # string, number, boolean, json
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Auditoria(Base):
    __tablename__ = "auditoria"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    caso_id = Column(Integer, ForeignKey("casos.id"))
    accion = Column(String(100), nullable=False)  # crear, actualizar, eliminar, etc.
    entidad = Column(String(100), nullable=False)  # caso, usuario, escalamiento, etc.
    entidad_id = Column(Integer)
    detalles = Column(Text)  # JSON con detalles del cambio
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    usuario = relationship("Usuario", back_populates="auditorias")
    caso = relationship("Caso", back_populates="auditorias")
