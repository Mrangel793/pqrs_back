from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional, Any
from datetime import datetime, timedelta
import uuid

from app.models.models import Caso, CasoIdentificador
from app.schemas.caso import CasoCreate, CasoUpdate, CasoFilter
from app.core.exceptions import NotFoundException


def create_caso(db: Session, caso: CasoCreate) -> Caso:
    """Crear nuevo caso"""
    # 1. Mapear datos básicos
    db_caso = Caso(
        radicado=caso.radicado,
        fechaRecepcion=caso.fechaRecepcion,
        fechaVencimiento=caso.fechaVencimiento,
        
        peticionarioNombre=caso.peticionarioNombre,
        peticionarioCorreo=caso.peticionarioCorreo,
        
        detalleSolicitud=caso.detalleSolicitud,
        tipoTramite=caso.tipoTramite,
        
        estadoCasoId=caso.estadoCasoId,
        semaforoId=caso.semaforoId,
        responsableId=caso.responsableId,
        
        destinatarioCorreo=caso.destinatarioCorreo,
        
        # Opcionales
        fechaEscalamientoTecnologia=caso.fechaEscalamientoTecnologia,
        respuestaContenido=caso.respuestaContenido,
        respuestaTextoAdicional=caso.respuestaTextoAdicional,
        tipoPDFId=caso.tipoPDFId,
        
        correoHiloId=caso.correoHiloId,
        correoMensajeSalidaId=caso.correoMensajeSalidaId,
        correoEnvioEstadoId=caso.correoEnvioEstadoId,
    )
    
    db.add(db_caso)
    db.flush() 

    # 2. Agregar Identificadores
    if caso.identificadores:
        for ident in caso.identificadores:
            db_ident = CasoIdentificador(
                casoId=db_caso.id,
                clave=ident.clave,
                valor=ident.valor
            )
            db.add(db_ident)

    db.commit()
    db.refresh(db_caso)
    return db_caso


def get_caso(db: Session, caso_id: uuid.UUID) -> Caso:
    """Obtener caso por ID"""
    caso = db.query(Caso).filter(Caso.id == caso_id).first()
    if not caso:
        raise NotFoundException(f"Caso {caso_id} no encontrado")
    return caso


def get_casos(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    filters: Optional[CasoFilter] = None
) -> List[Caso]:
    """Listar casos con filtros"""
    query = db.query(Caso)

    if filters:
        if filters.tipoTramite:
            query = query.filter(Caso.tipoTramite == filters.tipoTramite)
        if filters.estadoCasoId:
            query = query.filter(Caso.estadoCasoId == filters.estadoCasoId)
        if filters.semaforoId:
            query = query.filter(Caso.semaforoId == filters.semaforoId)
        if filters.responsableId:
            query = query.filter(Caso.responsableId == filters.responsableId)
        if filters.fechaDesde:
            query = query.filter(Caso.fechaRecepcion >= filters.fechaDesde)
        if filters.fechaHasta:
            query = query.filter(Caso.fechaRecepcion <= filters.fechaHasta)
        if filters.radicado:
            query = query.filter(Caso.radicado == filters.radicado)
            
        if filters.busqueda:
            search = f"%{filters.busqueda}%"
            query = query.filter(
                or_(
                    Caso.radicado.like(search),
                    Caso.peticionarioNombre.like(search),
                    Caso.detalleSolicitud.like(search),
                    Caso.peticionarioCorreo.like(search)
                )
            )

    return query.order_by(Caso.createdAt.desc()).offset(skip).limit(limit).all()


def update_caso(db: Session, caso_id: uuid.UUID, caso_update: CasoUpdate) -> Caso:
    """Actualizar caso"""
    db_caso = get_caso(db, caso_id)

    update_data = caso_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_caso, field, value)

    db.commit()
    db.refresh(db_caso)
    return db_caso


def delete_caso(db: Session, caso_id: uuid.UUID) -> bool:
    """Eliminar caso"""
    db_caso = get_caso(db, caso_id)
    db.delete(db_caso)
    db.commit()
    return True


def count_casos(db: Session, filters: Optional[CasoFilter] = None) -> int:
    """Contar casos"""
    query = db.query(Caso)
    if filters:
        if filters.tipoTramite:
            query = query.filter(Caso.tipoTramite == filters.tipoTramite)
        if filters.estadoCasoId:
            query = query.filter(Caso.estadoCasoId == filters.estadoCasoId)
        if filters.semaforoId:
            query = query.filter(Caso.semaforoId == filters.semaforoId)
        if filters.responsableId:
            query = query.filter(Caso.responsableId == filters.responsableId)
        if filters.radicado:
            query = query.filter(Caso.radicado == filters.radicado)
            
    return query.count()
