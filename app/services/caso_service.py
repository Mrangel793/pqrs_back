from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.models.models import Caso
from app.schemas.caso import CasoCreate, CasoUpdate, CasoFilter
from app.core.exceptions import NotFoundException


def generate_numero_caso() -> str:
    """Generar número único de caso"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"PQR-{timestamp}"


def create_caso(db: Session, caso: CasoCreate) -> Caso:
    """Crear nuevo caso"""
    db_caso = Caso(
        numero_caso=generate_numero_caso(),
        tipo=caso.tipo,
        asunto=caso.asunto,
        descripcion=caso.descripcion,
        estado="nuevo",
        prioridad=caso.prioridad,
        email_origen=caso.email_origen,
        usuario_asignado_id=caso.usuario_asignado_id,
        fecha_vencimiento=datetime.utcnow() + timedelta(days=15)
    )
    db.add(db_caso)
    db.commit()
    db.refresh(db_caso)
    return db_caso


def get_caso(db: Session, caso_id: int) -> Caso:
    """Obtener caso por ID"""
    caso = db.query(Caso).filter(Caso.id == caso_id).first()
    if not caso:
        raise NotFoundException(f"Caso {caso_id} no encontrado")
    return caso


def get_caso_by_numero(db: Session, numero_caso: str) -> Optional[Caso]:
    """Obtener caso por número"""
    return db.query(Caso).filter(Caso.numero_caso == numero_caso).first()


def get_casos(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    filters: Optional[CasoFilter] = None
) -> List[Caso]:
    """Listar casos con filtros"""
    query = db.query(Caso)

    if filters:
        if filters.tipo:
            query = query.filter(Caso.tipo == filters.tipo)
        if filters.estado:
            query = query.filter(Caso.estado == filters.estado)
        if filters.prioridad:
            query = query.filter(Caso.prioridad == filters.prioridad)
        if filters.usuario_asignado_id:
            query = query.filter(Caso.usuario_asignado_id == filters.usuario_asignado_id)
        if filters.fecha_desde:
            query = query.filter(Caso.fecha_recepcion >= filters.fecha_desde)
        if filters.fecha_hasta:
            query = query.filter(Caso.fecha_recepcion <= filters.fecha_hasta)
        if filters.busqueda:
            search = f"%{filters.busqueda}%"
            query = query.filter(
                (Caso.numero_caso.like(search)) |
                (Caso.asunto.like(search)) |
                (Caso.descripcion.like(search))
            )

    return query.offset(skip).limit(limit).all()


def update_caso(db: Session, caso_id: int, caso_update: CasoUpdate) -> Caso:
    """Actualizar caso"""
    db_caso = get_caso(db, caso_id)

    update_data = caso_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_caso, field, value)

    if caso_update.estado == "cerrado" and not db_caso.fecha_cierre:
        db_caso.fecha_cierre = datetime.utcnow()

    db.commit()
    db.refresh(db_caso)
    return db_caso


def delete_caso(db: Session, caso_id: int) -> bool:
    """Eliminar caso"""
    db_caso = get_caso(db, caso_id)
    db.delete(db_caso)
    db.commit()
    return True


def count_casos(db: Session, filters: Optional[CasoFilter] = None) -> int:
    """Contar casos con filtros"""
    query = db.query(Caso)

    if filters:
        if filters.tipo:
            query = query.filter(Caso.tipo == filters.tipo)
        if filters.estado:
            query = query.filter(Caso.estado == filters.estado)
        if filters.prioridad:
            query = query.filter(Caso.prioridad == filters.prioridad)

    return query.count()
