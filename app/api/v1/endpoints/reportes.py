from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any
from datetime import datetime, timedelta

from app.api.deps import get_db, get_current_user_dep
from app.models.models import Caso, Escalamiento

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
    casos_por_estado = db.query(
        Caso.estado,
        func.count(Caso.id)
    ).group_by(Caso.estado).all()

    # Casos por tipo
    casos_por_tipo = db.query(
        Caso.tipo,
        func.count(Caso.id)
    ).group_by(Caso.tipo).all()

    # Casos por prioridad
    casos_por_prioridad = db.query(
        Caso.prioridad,
        func.count(Caso.id)
    ).group_by(Caso.prioridad).all()

    # Escalamientos activos
    escalamientos_activos = db.query(func.count(Escalamiento.id)).filter(
        Escalamiento.estado == "pendiente"
    ).scalar()

    # Casos vencidos
    casos_vencidos = db.query(func.count(Caso.id)).filter(
        Caso.fecha_vencimiento < datetime.utcnow(),
        Caso.estado != "cerrado"
    ).scalar()

    # Casos creados últimos 7 días
    fecha_semana = datetime.utcnow() - timedelta(days=7)
    casos_ultima_semana = db.query(func.count(Caso.id)).filter(
        Caso.created_at >= fecha_semana
    ).scalar()

    return {
        "total_casos": total_casos,
        "casos_por_estado": {estado: count for estado, count in casos_por_estado},
        "casos_por_tipo": {tipo: count for tipo, count in casos_por_tipo},
        "casos_por_prioridad": {prioridad: count for prioridad, count in casos_por_prioridad},
        "escalamientos_activos": escalamientos_activos,
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
