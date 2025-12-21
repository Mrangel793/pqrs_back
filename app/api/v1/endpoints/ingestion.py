from fastapi import APIRouter, Depends, BackgroundTasks
from typing import Dict, Any

from app.api.deps import get_admin_user
from app.services.ingestion_service import ingestion_service

router = APIRouter()


@router.post("/process")
async def process_inbox_emails(
    background_tasks: BackgroundTasks,
    current_user = Depends(get_admin_user)
) -> Dict[str, Any]:
    """Procesar correos del buzón de entrada"""
    # Ejecutar en background
    result = await ingestion_service.process_inbox()
    return {
        "status": "completed",
        "result": result
    }


@router.post("/process-background")
async def process_inbox_background(
    background_tasks: BackgroundTasks,
    current_user = Depends(get_admin_user)
):
    """Procesar correos en segundo plano"""
    background_tasks.add_task(ingestion_service.process_inbox)
    return {
        "status": "processing",
        "message": "Procesamiento iniciado en segundo plano"
    }
