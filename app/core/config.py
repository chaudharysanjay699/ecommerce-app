from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    PROJECT_NAME: str = "Vidharthi Store"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str
    DB_ECHO: bool = False

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # OTP
    OTP_EXPIRE_MINUTES: int = 10

    # Firebase Cloud Messaging (FCM)
    FIREBASE_PROJECT_ID: str = ""
    # Either an absolute file path to serviceAccountKey.json
    # OR the raw JSON string of the service account (useful for Docker secrets / env vars)
    FIREBASE_SERVICE_ACCOUNT_JSON: str = ""

    # Email (SMTP via fastapi-mail)
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = ""          # e.g. noreply@yourdomain.com
    MAIL_FROM_NAME: str = "Vidharthi Store"
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_PORT: int = 587
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False

    # CORS
    BACKEND_CORS_ORIGINS: str = ""

    @model_validator(mode='after')
    def parse_cors_origins(self):
        """Parse CORS origins from string to list."""
        origins_value = self.BACKEND_CORS_ORIGINS
        
        if not origins_value:
            self.BACKEND_CORS_ORIGINS = []
            return self
            
        if isinstance(origins_value, list):
            self.BACKEND_CORS_ORIGINS = origins_value
            return self
            
        if isinstance(origins_value, str):
            # Try JSON array format first
            if origins_value.startswith("["):
                try:
                    import json
                    self.BACKEND_CORS_ORIGINS = json.loads(origins_value)
                    return self
                except Exception:
                    pass
            
            # Comma-separated format
            self.BACKEND_CORS_ORIGINS = [i.strip() for i in origins_value.split(",") if i.strip()]
            return self
        
        self.BACKEND_CORS_ORIGINS = []
        return self

    # File upload
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 5 MB
    
    # Server URL (for constructing file URLs dynamically)
    SERVER_URL: str = "http://localhost:8000"  # Override in production


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
