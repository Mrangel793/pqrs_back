from typing import Any, Dict
from datetime import datetime
import re


def format_date(date: datetime, format: str = "%d/%m/%Y") -> str:
    """Formatear fecha"""
    return date.strftime(format)


def format_datetime(dt: datetime, format: str = "%d/%m/%Y %H:%M") -> str:
    """Formatear fecha y hora"""
    return dt.strftime(format)


def clean_string(text: str) -> str:
    """Limpiar string de caracteres especiales"""
    return re.sub(r'[^\w\s-]', '', text).strip()


def validate_email(email: str) -> bool:
    """Validar formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def sanitize_filename(filename: str) -> str:
    """Sanitizar nombre de archivo"""
    # Eliminar caracteres no permitidos
    filename = re.sub(r'[^\w\s.-]', '', filename)
    # Reemplazar espacios por guiones bajos
    filename = filename.replace(' ', '_')
    return filename


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncar texto a longitud máxima"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def parse_priority(priority: str) -> int:
    """Convertir prioridad a número"""
    priority_map = {
        "baja": 1,
        "media": 2,
        "alta": 3,
        "critica": 4
    }
    return priority_map.get(priority.lower(), 2)


def format_file_size(size_bytes: int) -> str:
    """Formatear tamaño de archivo"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def build_filter_query(filters: Dict[str, Any]) -> Dict[str, Any]:
    """Construir diccionario de filtros eliminando None"""
    return {k: v for k, v in filters.items() if v is not None}
