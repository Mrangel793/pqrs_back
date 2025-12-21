from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db, get_current_user_dep, get_admin_user
from app.schemas.usuario import UsuarioCreate, UsuarioResponse, UsuarioUpdate
from app.models.models import Usuario
from app.core.security import get_password_hash

router = APIRouter()


@router.get("/", response_model=List[UsuarioResponse])
async def list_usuarios(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_dep)
):
    """Listar usuarios"""
    usuarios = db.query(Usuario).offset(skip).limit(limit).all()
    return usuarios


@router.get("/{usuario_id}", response_model=UsuarioResponse)
async def get_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_dep)
):
    """Obtener usuario por ID"""
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def create_usuario(
    usuario: UsuarioCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """Crear nuevo usuario"""
    # Verificar si ya existe
    existing = db.query(Usuario).filter(Usuario.username == usuario.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="El usuario ya existe")

    db_usuario = Usuario(
        username=usuario.username,
        email=usuario.email,
        hashed_password=get_password_hash(usuario.password),
        nombre_completo=usuario.nombre_completo,
        rol=usuario.rol
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario


@router.put("/{usuario_id}", response_model=UsuarioResponse)
async def update_usuario(
    usuario_id: int,
    usuario_update: UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """Actualizar usuario"""
    db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    update_data = usuario_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_usuario, field, value)

    db.commit()
    db.refresh(db_usuario)
    return db_usuario


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """Eliminar usuario"""
    db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    db.delete(db_usuario)
    db.commit()
    return None
