from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List
import json


class Settings(BaseSettings):
    """Configuración de la aplicación"""

    # App
    APP_NAME: str = "Sistema PQR Escaladas"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 8
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Microsoft Graph
    MICROSOFT_CLIENT_ID: Optional[str] = None
    MICROSOFT_CLIENT_SECRET: Optional[str] = None
    MICROSOFT_TENANT_ID: Optional[str] = None
    MAILBOX_ADDRESS: Optional[str] = None

    # File Upload
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 10

    # CORS
    CORS_ORIGINS: str = '["http://localhost:5173"]'

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow"
    )

    @property
    def cors_origins_list(self) -> List[str]:
        """Parsear CORS_ORIGINS de JSON string a lista"""
        try:
            return json.loads(self.CORS_ORIGINS)
        except (json.JSONDecodeError, TypeError):
            return ["http://localhost:5173"]


settings = Settings()
