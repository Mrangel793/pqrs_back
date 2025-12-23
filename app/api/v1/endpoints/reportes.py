from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any
from datetime import datetime, timedelta

from app.api.deps import get_db, get_current_user_dep
from app.models.models import Caso, Escalamiento, EstadoCaso, Semaforo

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_dep)
) -> Dict[str, Any]:
    """Obtener estadísticas para el dashboard"""

    # Total de casos
    total_casos = db.query(func.count(Caso.id)).scalar()

    # Casos por estado
    # Join con EstadoCaso para obtener nombre si fuera necesario, o solo agrupar por ID
    # Aquí tratamos de obtener el nombre si es posible, si no, ID
    casos_por_estado_query = db.query(
        EstadoCaso.descripcion,
        func.count(Caso.id)
    ).join(EstadoCaso, Caso.estadoCasoId == EstadoCaso.id).group_by(EstadoCaso.descripcion).all()
    
    casos_por_estado = {desc: count for desc, count in casos_por_estado_query}

    # Casos por tipo trámite
    # Nota: TipoTramite es string en Caso ("tipoTramite"), pero si hubiera tabla catalogo...
    # En el modelo Caso, 'tipoTramite' es string. En el SQL habia 'tab_tipotramite'? 
    # Revisando models.py: `tipoTramite = Column(String(50))` en Caso.
    # No hay FK a TipoTramite en Caso en mi models.py actualizado (checkear).
    # Si es string, agrupamos por string.
    casos_por_tipo_query = db.query(
        Caso.tipoTramite,
        func.count(Caso.id)
    ).group_by(Caso.tipoTramite).all()
    
    casos_por_tipo = {tipo: count for tipo, count in casos_por_tipo_query}

    # Casos por semáforo (prioridad)
    casos_por_semaforo_query = db.query(
        Semaforo.colorHex, # O descripcion/nombre
        func.count(Caso.id)
    ).join(Semaforo, Caso.semaforoId == Semaforo.id).group_by(Semaforo.colorHex).all()
    
    casos_por_prioridad = {color: count for color, count in casos_por_semaforo_query}

    # Escalamientos (Total)
    escalamientos_total = db.query(func.count(Escalamiento.id)).scalar()

    # Casos vencidos (fechaVencimiento < now y estado no cerrado)
    # Asumimos estado cerrado tiene algun ID o flag 'activo' en EstadoCaso?
    # EstadoCaso tiene 'activo' boolean, pero eso es si el estado está habilitado en catalogo.
    # Necesitamos saber qué ID es "cerrado". Por ahora chequeamos solo fecha.
    casos_vencidos = db.query(func.count(Caso.id)).filter(
        Caso.fechaVencimiento < datetime.utcnow()
        # , Caso.estadoCasoId != ID_CERRADO # TODO: Definir ID cerrado
    ).scalar()

    # Casos creados últimos 7 días
    fecha_semana = datetime.utcnow() - timedelta(days=7)
    casos_ultima_semana = db.query(func.count(Caso.id)).filter(
        Caso.createdAt >= fecha_semana
    ).scalar()

    return {
        "total_casos": total_casos,
        "casos_por_estado": casos_por_estado,
        "casos_por_tipo": casos_por_tipo,
        "casos_por_prioridad": casos_por_prioridad,
        "escalamientos_total": escalamientos_total,
        "casos_vencidos": casos_vencidos,
        "casos_ultima_semana": casos_ultima_semana
    }


@router.get("/casos-mensuales")
async def get_casos_mensuales(
    meses: int = 12,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_dep)
):
    """Obtener casos por mes"""
    # Simplificado - implementar lógica completa según necesidades
    return {"message": "Reporte de casos mensuales"}


@router.get("/tiempos-respuesta")
async def get_tiempos_respuesta(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_dep)
):
    """Obtener métricas de tiempos de respuesta"""
    return {"message": "Reporte de tiempos de respuesta"}
