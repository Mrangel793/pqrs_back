from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# ==========================================
# Esquemas para Usuarios
# ==========================================

class UsuarioBase(BaseModel):
    """Schema base de usuario"""
    nombre: str
    correo: EmailStr
    activo: Optional[bool] = True

class UsuarioCreate(UsuarioBase):
    """Schema para crear usuario"""
    password: str

class UsuarioUpdate(BaseModel):
    """Schema para actualizar usuario"""
    nombre: Optional[str] = None
    correo: Optional[EmailStr] = None
    activo: Optional[bool] = None
    password: Optional[str] = None

class UsuarioResponse(UsuarioBase):
    """Schema de respuesta de usuario"""
    id: int
    activo: bool
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True

# Login & Tokens
class UsuarioLogin(BaseModel):
    correo: str
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    correo: Optional[str] = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str

