from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.usuario import Token, UsuarioLogin
from app.core.security import verify_password, create_access_token

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Endpoint de login"""
    # Aquí deberías buscar el usuario en la base de datos
    # from app.models.models import Usuario
    # user = db.query(Usuario).filter(Usuario.username == form_data.username).first()

    # Por ahora, autenticación simulada
    if form_data.username != "admin" or form_data.password != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Crear token
    access_token = create_access_token(data={"sub": "1", "username": form_data.username})

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/refresh", response_model=Token)
async def refresh_token(current_user = Depends(get_db)):
    """Refrescar token de acceso"""
    # Implementar lógica de refresh token
    pass
