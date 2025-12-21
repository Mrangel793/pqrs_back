from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UsuarioBase(BaseModel):
    """Schema base de usuario"""
    username: str
    email: EmailStr
    nombre_completo: Optional[str] = None
    rol: str


class UsuarioCreate(UsuarioBase):
    """Schema para crear usuario"""
    password: str


class UsuarioUpdate(BaseModel):
    """Schema para actualizar usuario"""
    email: Optional[EmailStr] = None
    nombre_completo: Optional[str] = None
    rol: Optional[str] = None
    activo: Optional[bool] = None


class UsuarioResponse(UsuarioBase):
    """Schema de respuesta de usuario"""
    id: int
    activo: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UsuarioLogin(BaseModel):
    """Schema para login"""
    username: str
    password: str


class Token(BaseModel):
    """Schema de token"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Datos del token"""
    username: Optional[str] = None
