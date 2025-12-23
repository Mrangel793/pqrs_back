from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, List
import logging

from app.models.models import Sesion, Usuario
from app.schemas.sesion import SesionCreate, SesionInDB

logger = logging.getLogger(__name__)


class SessionService:
    """Servicio para gestionar sesiones de usuario"""
    
    @staticmethod
    def create_session(
        db: Session,
        usuario_id: int,
        token: str,
        expiration_hours: int,
        ip_origen: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Optional[Sesion]:
        """
        Crear un nuevo registro de sesión en la base de datos.
        
        Args:
            db: Sesión de base de datos
            usuario_id: ID del usuario autenticado
            token: Access token JWT generado
            expiration_hours: Horas hasta la expiración del token
            ip_origen: IP del cliente (opcional)
            user_agent: User agent del navegador (opcional)
            
        Returns:
            Objeto Sesion creado o None si hay error
        """
        try:
            # Verificar que el usuario existe
            usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
            if not usuario:
                logger.error(f"Usuario {usuario_id} no encontrado al crear sesión")
                return None
            
            # Calcular fecha de expiración
            fecha_expiracion = datetime.now() + timedelta(hours=expiration_hours)
            
            # Crear nueva sesión
            nueva_sesion = Sesion(
                usuarioId=usuario_id,
                token=token[:500],  # Limitar a 500 caracteres
                fechaExpiracion=fecha_expiracion,
                activa=True,
                ipOrigen=ip_origen,
                userAgent=user_agent
            )
            
            db.add(nueva_sesion)
            db.commit()
            db.refresh(nueva_sesion)
            
            logger.info(f"Sesión creada exitosamente para usuario {usuario_id}")
            return nueva_sesion
            
        except Exception as e:
            logger.error(f"Error al crear sesión para usuario {usuario_id}: {str(e)}")
            db.rollback()
            return None
    
    @staticmethod
    def get_active_sessions(
        db: Session,
        usuario_id: int
    ) -> List[Sesion]:
        """
        Obtener todas las sesiones activas de un usuario.
        
        Args:
            db: Sesión de base de datos
            usuario_id: ID del usuario
            
        Returns:
            Lista de sesiones activas
        """
        try:
            return db.query(Sesion).filter(
                Sesion.usuarioId == usuario_id,
                Sesion.activa == True,
                Sesion.fechaExpiracion > datetime.now()
            ).order_by(Sesion.fechaCreacion.desc()).all()
        except Exception as e:
            logger.error(f"Error al obtener sesiones activas: {str(e)}")
            return []
    
    @staticmethod
    def invalidate_session(
        db: Session,
        session_id: str
    ) -> bool:
        """
        Invalidar una sesión (marcarla como inactiva).
        
        Args:
            db: Sesión de base de datos
            session_id: UUID de la sesión
            
        Returns:
            True si se invalidó exitosamente, False en caso contrario
        """
        try:
            sesion = db.query(Sesion).filter(Sesion.id == session_id).first()
            if sesion:
                sesion.activa = False
                db.commit()
                logger.info(f"Sesión {session_id} invalidada")
                return True
            return False
        except Exception as e:
            logger.error(f"Error al invalidar sesión {session_id}: {str(e)}")
            db.rollback()
            return False
    
    @staticmethod
    def invalidate_user_sessions(
        db: Session,
        usuario_id: int
    ) -> int:
        """
        Invalidar todas las sesiones activas de un usuario.
        
        Args:
            db: Sesión de base de datos
            usuario_id: ID del usuario
            
        Returns:
            Número de sesiones invalidadas
        """
        try:
            result = db.query(Sesion).filter(
                Sesion.usuarioId == usuario_id,
                Sesion.activa == True
            ).update({"activa": False})
            db.commit()
            logger.info(f"{result} sesiones invalidadas para usuario {usuario_id}")
            return result
        except Exception as e:
            logger.error(f"Error al invalidar sesiones del usuario {usuario_id}: {str(e)}")
            db.rollback()
            return 0
    
    @staticmethod
    def cleanup_expired_sessions(db: Session) -> int:
        """
        Limpiar sesiones expiradas (marcarlas como inactivas).
        Útil para tareas de mantenimiento programadas.
        
        Args:
            db: Sesión de base de datos
            
        Returns:
            Número de sesiones limpiadas
        """
        try:
            result = db.query(Sesion).filter(
                Sesion.fechaExpiracion < datetime.now(),
                Sesion.activa == True
            ).update({"activa": False})
            db.commit()
            logger.info(f"{result} sesiones expiradas limpiadas")
            return result
        except Exception as e:
            logger.error(f"Error al limpiar sesiones expiradas: {str(e)}")
            db.rollback()
            return 0
