from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    usuarios,
    casos,
    escalamientos,
    adjuntos,
    pdf,
    correo,
    configuracion,
    auditoria,
    reportes,
    ingestion
)

api_router = APIRouter()

# Incluir routers de endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
api_router.include_router(usuarios.router, prefix="/usuarios", tags=["Usuarios"])
api_router.include_router(casos.router, prefix="/casos", tags=["Casos"])
api_router.include_router(escalamientos.router, prefix="/escalamientos", tags=["Escalamientos"])
api_router.include_router(adjuntos.router, prefix="/adjuntos", tags=["Adjuntos"])
api_router.include_router(pdf.router, prefix="/pdf", tags=["PDFs"])
api_router.include_router(correo.router, prefix="/correo", tags=["Correo"])
api_router.include_router(configuracion.router, prefix="/configuracion", tags=["Configuración"])
api_router.include_router(auditoria.router, prefix="/auditoria", tags=["Auditoría"])
api_router.include_router(reportes.router, prefix="/reportes", tags=["Reportes"])
api_router.include_router(ingestion.router, prefix="/ingestion", tags=["Ingesta"])
