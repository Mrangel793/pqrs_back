from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import os
import uuid

from app.api.deps import get_db, get_current_user_dep
from app.schemas.adjunto import AdjuntoResponse
from app.models.models import Adjunto, Caso
from app.services.storage_service import storage_service
from app.core.exceptions import FileUploadException

router = APIRouter()


@router.get("/caso/{caso_id}", response_model=List[AdjuntoResponse])
async def list_adjuntos_caso(
    caso_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_dep)
):
    """Listar adjuntos de un caso"""
    adjuntos = db.query(Adjunto).filter(Adjunto.casoId == caso_id).all()
    return adjuntos


@router.get("/{adjunto_id}")
async def download_adjunto(
    adjunto_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_dep)
):
    """Descargar adjunto"""
    adjunto = db.query(Adjunto).filter(Adjunto.id == adjunto_id).first()
    if not adjunto:
        raise HTTPException(status_code=404, detail="Adjunto no encontrado")

    if not os.path.exists(adjunto.rutaStorage):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    return FileResponse(
        path=adjunto.rutaStorage,
        filename=adjunto.nombreArchivo,
        media_type=adjunto.mimeType
    )


@router.post("/", response_model=AdjuntoResponse, status_code=status.HTTP_201_CREATED)
async def upload_adjunto(
    caso_id: uuid.UUID = Form(...),
    tipo_adjunto_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_dep)
):
    """Subir adjunto a un caso"""
    # Verificar que el caso existe
    caso = db.query(Caso).filter(Caso.id == caso_id).first()
    if not caso:
        raise HTTPException(status_code=404, detail="Caso no encontrado")

    # Leer contenido del archivo
    content = await file.read()

    # Validar tamaño (usando servicio o lógica inline si el servicio falla)
    if hasattr(storage_service, 'validate_file_size') and not storage_service.validate_file_size(len(content)):
        raise FileUploadException("El archivo excede el tamaño máximo permitido")

    # Guardar archivo
    # Pasamos str(caso_id) porque storage_service probablemente espera string para paths
    file_path = await storage_service.save_file(content, file.filename, str(caso_id))

    # Crear registro en BD
    db_adjunto = Adjunto(
        casoId=caso_id,
        tipoAdjuntoId=tipo_adjunto_id,
        nombreArchivo=file.filename,
        mimeType=file.content_type,
        tamanioBytes=len(content),
        rutaStorage=file_path,
        version=1 
    )
    db.add(db_adjunto)
    db.commit()
    db.refresh(db_adjunto)

    return db_adjunto


@router.delete("/{adjunto_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_adjunto(
    adjunto_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_dep)
):
    """Eliminar adjunto"""
    adjunto = db.query(Adjunto).filter(Adjunto.id == adjunto_id).first()
    if not adjunto:
        raise HTTPException(status_code=404, detail="Adjunto no encontrado")

    # Eliminar archivo
    await storage_service.delete_file(adjunto.rutaStorage)

    # Eliminar registro
    db.delete(adjunto)
    db.commit()

    return None
