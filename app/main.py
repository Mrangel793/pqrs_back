from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from app.config import settings
from app.api.v1.router import api_router
from app.core.scheduler import start_scheduler, stop_scheduler
from app.database import verify_connection, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestionar ciclo de vida de la aplicación"""
    # Startup
    print(f"🚀 Iniciando {settings.APP_NAME}...")

    # Verificar conexión a base de datos
    print("📊 Verificando conexión a base de datos...")
    if verify_connection():
        print("✅ Conexión a base de datos exitosa")
    else:
        print("⚠️  Advertencia: No se pudo conectar a la base de datos")

    # Iniciar scheduler para tareas programadas
    print("⏰ Iniciando scheduler de tareas...")
    start_scheduler()

    print(f"✨ {settings.APP_NAME} iniciado correctamente")
    print(f"📚 Documentación disponible en: /docs")
    print(f"🔍 Health check disponible en: /health")

    yield

    # Shutdown
    print(f"👋 Cerrando {settings.APP_NAME}...")

    # Detener scheduler
    print("⏰ Deteniendo scheduler...")
    stop_scheduler()

    # Cerrar conexiones de base de datos
    print("📊 Cerrando conexiones a base de datos...")
    engine.dispose()

    print(f"✅ {settings.APP_NAME} detenido correctamente")


# Crear aplicación FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="API para gestión de Peticiones, Quejas y Reclamos (PQR) escaladas",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configurar CORS desde settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar directorio de uploads para servir archivos estáticos
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Incluir router principal en /api/v1
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root():
    """Endpoint raíz - Información de la API"""
    return {
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "message": "API de gestión de PQR escaladas",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health"
    }


@app.get("/health", tags=["Health"], status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check endpoint - Verificar estado del servicio

    Retorna:
        - status: Estado del servicio (healthy/unhealthy)
        - app: Nombre de la aplicación
        - database: Estado de la conexión a base de datos
    """
    # Verificar conexión a base de datos
    db_status = verify_connection()

    return {
        "status": "healthy" if db_status else "unhealthy",
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "database": "connected" if db_status else "disconnected"
    }
