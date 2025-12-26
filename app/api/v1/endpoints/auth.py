from fastapi import APIRouter, Depends, HTTPException, status, Body, Request
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.usuario import Token, UsuarioLogin, RefreshTokenRequest, LoginResponse
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.services.session_service import SessionService
from app.utils.request_utils import get_client_ip, get_user_agent
from app.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(
    request: Request,
    user_data: UsuarioLogin,
    db: Session = Depends(get_db)
):
    """Endpoint de login"""
    # Buscar usuario por correo
    from app.models.models import Usuario
    user = db.query(Usuario).filter(Usuario.correo == user_data.correo).first()

    # Verificar credenciales
    if not user or not verify_password(user_data.password, user.passwordHash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verificar si está activo
    if not user.activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario está inactivo"
        )

    # Crear tokens
    access_token = create_access_token(data={"sub": str(user.id), "email": user.correo})
    refresh_token = create_refresh_token(data={"sub": str(user.id), "email": user.correo})

    # Crear registro de sesión
    try:
        ip_origen = get_client_ip(request)
        user_agent = get_user_agent(request)
        
        session = SessionService.create_session(
            db=db,
            usuario_id=user.id,
            token=access_token,
            expiration_hours=settings.ACCESS_TOKEN_EXPIRE_HOURS,
            ip_origen=ip_origen,
            user_agent=user_agent
        )
        
        if session:
            logger.info(f"Sesión creada para usuario {user.id} desde IP {ip_origen}")
        else:
            logger.warning(f"No se pudo crear sesión para usuario {user.id}, pero login exitoso")
    except Exception as e:
        # No bloquear el login si falla la creación de sesión
        logger.error(f"Error al crear sesión para usuario {user.id}: {str(e)}")

    return {
        "user": user,
        "token": {
            "access_token": access_token, 
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: Request,
    request_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Refrescar token de acceso"""
    refresh_token = request_data.refresh_token
    try:
        from app.core.security import decode_token
        payload = decode_token(refresh_token)
        
        # Verificar que sea un refresh token
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
            )
            
        # Verificar usuario
        from app.models.models import Usuario
        user = db.query(Usuario).filter(Usuario.id == user_id).first()
        
        if not user or not user.activo:
             raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado o inactivo",
            )
            
        # Crear nuevos tokens
        new_access_token = create_access_token(data={"sub": str(user.id), "email": user.correo})
        # Opcional: Rotar refresh token también (mayor seguridad)
        new_refresh_token = create_refresh_token(data={"sub": str(user.id), "email": user.correo})
        
        # Crear registro de sesión para el nuevo access token
        try:
            ip_origen = get_client_ip(request)
            user_agent = get_user_agent(request)
            
            session = SessionService.create_session(
                db=db,
                usuario_id=user.id,
                token=new_access_token,
                expiration_hours=settings.ACCESS_TOKEN_EXPIRE_HOURS,
                ip_origen=ip_origen,
                user_agent=user_agent
            )
            
            if session:
                logger.info(f"Nueva sesión creada al refrescar token para usuario {user.id}")
            else:
                logger.warning(f"No se pudo crear sesión al refrescar token para usuario {user.id}")
        except Exception as e:
            logger.error(f"Error al crear sesión en refresh para usuario {user.id}: {str(e)}")
        
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo validar las credenciales",
        )
