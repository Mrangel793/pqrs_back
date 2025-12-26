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
    usuarios = db.query(Usuario).order_by(Usuario.id).offset(skip).limit(limit).all()
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
    existing = db.query(Usuario).filter(Usuario.correo == usuario.correo).first()
    if existing:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    db_usuario = Usuario(
        nombre=usuario.nombre,
        correo=usuario.correo,
        passwordHash=get_password_hash(usuario.password),
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
    
    # Manejo especial para contraseña
    if "password" in update_data:
        password = update_data.pop("password")
        if password:
             db_usuario.passwordHash = get_password_hash(password)

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
