from typing import Generator
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.core.security import get_current_active_user


def get_db() -> Generator:
    """Dependency para obtener sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user_dep(current_user = Depends(get_current_active_user)):
    """Dependency para obtener usuario actual"""
    return current_user


def get_admin_user(current_user = Depends(get_current_active_user)):
    """Dependency para verificar usuario admin"""
    if current_user.get("rol") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos de administrador"
        )
    return current_user


def get_client_info(request: Request):
    """Obtener información del cliente para auditoría"""
    return {
        "ip_address": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent")
    }
