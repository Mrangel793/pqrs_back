from fastapi import HTTPException, status


class PQRException(Exception):
    """Excepción base para el sistema PQR"""
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundException(PQRException):
    """Recurso no encontrado"""
    def __init__(self, message: str = "Recurso no encontrado"):
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class UnauthorizedException(PQRException):
    """No autorizado"""
    def __init__(self, message: str = "No autorizado"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class ForbiddenException(PQRException):
    """Prohibido"""
    def __init__(self, message: str = "Acceso prohibido"):
        super().__init__(message, status.HTTP_403_FORBIDDEN)


class BadRequestException(PQRException):
    """Solicitud incorrecta"""
    def __init__(self, message: str = "Solicitud incorrecta"):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class ConflictException(PQRException):
    """Conflicto"""
    def __init__(self, message: str = "Conflicto con el estado actual"):
        super().__init__(message, status.HTTP_409_CONFLICT)


class ValidationException(PQRException):
    """Error de validación"""
    def __init__(self, message: str = "Error de validación"):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY)


class DatabaseException(PQRException):
    """Error de base de datos"""
    def __init__(self, message: str = "Error en la base de datos"):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)


class EmailException(PQRException):
    """Error al enviar correo"""
    def __init__(self, message: str = "Error al enviar correo electrónico"):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)


class FileUploadException(PQRException):
    """Error al subir archivo"""
    def __init__(self, message: str = "Error al subir archivo"):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class PDFGenerationException(PQRException):
    """Error al generar PDF"""
    def __init__(self, message: str = "Error al generar PDF"):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)
