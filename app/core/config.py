from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    APP_NAME: str = "FileMonitor"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    WATCH_PATH: Path = Path("./monitored_files")
    
    # Database settings
    DATABASE_URL: str = "postgresql://user:password@localhost/fa_db"
    
    # Security settings
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # PPOB settings
    PPOB_API_URL: str = "https://api.ppob-provider.com"
    PPOB_API_KEY: str = "your-ppob-api-key"
    PPOB_TIMEOUT: int = 30
    
    # Midtrans settings
    MIDTRANS_SERVER_KEY: str = "your-midtrans-server-key"
    MIDTRANS_CLIENT_KEY: str = "your-midtrans-client-key"
    MIDTRANS_IS_PRODUCTION: bool = False
    MIDTRANS_MERCHANT_ID: str = "your-merchant-id"
    
    # Admin settings
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"
    
    class Config:
        env_file = ".env"

settings = Settings()
