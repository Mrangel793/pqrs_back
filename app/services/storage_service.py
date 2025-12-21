import os
import base64
import aiofiles
from datetime import datetime
from typing import Optional
import uuid

from app.config import settings
from app.core.exceptions import FileUploadException


class StorageService:
    """Servicio para almacenamiento de archivos"""

    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        self.ensure_upload_dir()

    def ensure_upload_dir(self):
        """Asegurar que exista el directorio de uploads"""
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)

    def get_caso_directory(self, caso_id: int) -> str:
        """Obtener directorio para un caso específico"""
        caso_dir = os.path.join(self.upload_dir, f"caso_{caso_id}")
        if not os.path.exists(caso_dir):
            os.makedirs(caso_dir)
        return caso_dir

    async def save_file(
        self,
        file_content: bytes,
        filename: str,
        caso_id: Optional[int] = None
    ) -> str:
        """Guardar archivo en disco"""
        try:
            # Determinar directorio de destino
            if caso_id:
                target_dir = self.get_caso_directory(caso_id)
            else:
                target_dir = self.upload_dir

            # Generar nombre único
            unique_filename = self.generate_unique_filename(filename)
            file_path = os.path.join(target_dir, unique_filename)

            # Guardar archivo
            async with aiofiles.open(file_path, "wb") as f:
                await f.write(file_content)

            return file_path

        except Exception as e:
            raise FileUploadException(f"Error guardando archivo: {str(e)}")

    def save_attachment(
        self,
        content_bytes: str,
        filename: str,
        caso_id: int
    ) -> str:
        """Guardar adjunto de correo (base64)"""
        try:
            # Decodificar base64
            file_content = base64.b64decode(content_bytes)

            # Determinar directorio
            caso_dir = self.get_caso_directory(caso_id)

            # Generar nombre único
            unique_filename = self.generate_unique_filename(filename)
            file_path = os.path.join(caso_dir, unique_filename)

            # Guardar archivo
            with open(file_path, "wb") as f:
                f.write(file_content)

            return file_path

        except Exception as e:
            raise FileUploadException(f"Error guardando adjunto: {str(e)}")

    def generate_unique_filename(self, original_filename: str) -> str:
        """Generar nombre único para archivo"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        name, ext = os.path.splitext(original_filename)

        # Limpiar nombre de archivo
        clean_name = "".join(c for c in name if c.isalnum() or c in "._- ")
        return f"{clean_name}_{timestamp}_{unique_id}{ext}"

    async def delete_file(self, file_path: str) -> bool:
        """Eliminar archivo"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            raise FileUploadException(f"Error eliminando archivo: {str(e)}")

    def get_file_size(self, file_path: str) -> int:
        """Obtener tamaño de archivo en bytes"""
        if os.path.exists(file_path):
            return os.path.getsize(file_path)
        return 0

    def validate_file_size(self, file_size: int) -> bool:
        """Validar tamaño de archivo"""
        max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024  # Convertir a bytes
        return file_size <= max_size


storage_service = StorageService()
