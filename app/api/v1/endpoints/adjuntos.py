from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import os

from app.api.deps import get_db, get_current_user_dep
from app.schemas.adjunto import AdjuntoResponse, AdjuntoCreate
from app.models.models import Adjunto, Caso
from app.services.storage_service import storage_service
from app.core.exceptions import FileUploadException

router = APIRouter()


@router.get("/caso/{caso_id}", response_model=List[AdjuntoResponse])
async def list_adjuntos_caso(
    caso_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_dep)
):
    """Listar adjuntos de un caso"""
    adjuntos = db.query(Adjunto).filter(Adjunto.caso_id == caso_id).all()
    return adjuntos


@router.get("/{adjunto_id}")
async def download_adjunto(
    adjunto_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_dep)
):
    """Descargar adjunto"""
    adjunto = db.query(Adjunto).filter(Adjunto.id == adjunto_id).first()
    if not adjunto:
        raise HTTPException(status_code=404, detail="Adjunto no encontrado")

    if not os.path.exists(adjunto.ruta_archivo):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    return FileResponse(
        path=adjunto.ruta_archivo,
        filename=adjunto.nombre_archivo,
        media_type=adjunto.tipo_mime
    )


@router.post("/", response_model=AdjuntoResponse, status_code=status.HTTP_201_CREATED)
async def upload_adjunto(
    caso_id: int,
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

    # Validar tamaño
    if not storage_service.validate_file_size(len(content)):
        raise FileUploadException("El archivo excede el tamaño máximo permitido")

    # Guardar archivo
    file_path = await storage_service.save_file(content, file.filename, caso_id)

    # Crear registro en BD
    db_adjunto = Adjunto(
        caso_id=caso_id,
        nombre_archivo=file.filename,
        ruta_archivo=file_path,
        tipo_mime=file.content_type,
        tamano=len(content)
    )
    db.add(db_adjunto)
    db.commit()
    db.refresh(db_adjunto)

    return db_adjunto


@router.delete("/{adjunto_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_adjunto(
    adjunto_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_dep)
):
    """Eliminar adjunto"""
    adjunto = db.query(Adjunto).filter(Adjunto.id == adjunto_id).first()
    if not adjunto:
        raise HTTPException(status_code=404, detail="Adjunto no encontrado")

    # Eliminar archivo
    await storage_service.delete_file(adjunto.ruta_archivo)

    # Eliminar registro
    db.delete(adjunto)
    db.commit()

    return None
