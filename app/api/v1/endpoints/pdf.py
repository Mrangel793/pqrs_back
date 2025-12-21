from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from typing import Dict, Any

from app.api.deps import get_current_user_dep
from app.services.pdf_service import pdf_service
from app.core.exceptions import PDFGenerationException

router = APIRouter()


@router.post("/factura")
async def generate_factura_pdf(
    data: Dict[str, Any],
    current_user = Depends(get_current_user_dep)
):
    """Generar PDF de factura"""
    try:
        pdf_path = pdf_service.generate_factura_pdf(data)
        return FileResponse(
            path=pdf_path,
            filename=f"factura_{data.get('numero_factura')}.pdf",
            media_type="application/pdf"
        )
    except PDFGenerationException as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/postilla-apostilla")
async def generate_postilla_apostilla_pdf(
    data: Dict[str, Any],
    current_user = Depends(get_current_user_dep)
):
    """Generar PDF de postilla/apostilla"""
    try:
        pdf_path = pdf_service.generate_postilla_apostilla_pdf(data)
        return FileResponse(
            path=pdf_path,
            filename=f"postilla_{data.get('numero_caso')}.pdf",
            media_type="application/pdf"
        )
    except PDFGenerationException as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/falla-no-respuesta")
async def generate_falla_no_respuesta_pdf(
    data: Dict[str, Any],
    current_user = Depends(get_current_user_dep)
):
    """Generar PDF de falla/no respuesta"""
    try:
        pdf_path = pdf_service.generate_falla_no_respuesta_pdf(data)
        return FileResponse(
            path=pdf_path,
            filename=f"falla_{data.get('numero_caso')}.pdf",
            media_type="application/pdf"
        )
    except PDFGenerationException as e:
        raise HTTPException(status_code=500, detail=str(e))
