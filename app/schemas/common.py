from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ResponseBase(BaseModel):
    """Schema base para respuestas"""
    success: bool = True
    message: str
    data: Optional[dict] = None


class PaginationParams(BaseModel):
    """Parámetros de paginación"""
    page: int = 1
    page_size: int = 10

    class Config:
        json_schema_extra = {
            "example": {
                "page": 1,
                "page_size": 10
            }
        }


class PaginatedResponse(BaseModel):
    """Respuesta paginada"""
    items: list
    total: int
    page: int
    page_size: int
    total_pages: int
