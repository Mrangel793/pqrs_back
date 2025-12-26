from fastapi import Request
from typing import Optional


def get_client_ip(request: Request) -> Optional[str]:
    """
    Extraer la IP del cliente del request.
    Considera proxies y headers de forwarding.
    
    Args:
        request: FastAPI Request object
        
    Returns:
        IP del cliente o None si no se puede determinar
    """
    # Intentar obtener IP de headers de proxy primero
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # X-Forwarded-For puede contener múltiples IPs, tomar la primera
        return forwarded_for.split(",")[0].strip()
    
    # Intentar X-Real-IP
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    
    # Fallback a la IP directa del cliente
    if request.client:
        return request.client.host
    
    return None


def get_user_agent(request: Request) -> Optional[str]:
    """
    Extraer el User-Agent del request.
    
    Args:
        request: FastAPI Request object
        
    Returns:
        User-Agent string o None si no está presente
    """
    user_agent = request.headers.get("User-Agent")
    if user_agent:
        # Limitar a 500 caracteres para que quepa en la columna de DB
        return user_agent[:500]
    
    return None
