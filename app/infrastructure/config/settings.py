from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path
from app.infrastructure.config.auth_config import auth_config

class Settings(BaseSettings):
    """
    Main application settings yang mengintegrasikan semua domain configs.
    Mengimplementasikan Single Responsibility Principle dengan memisahkan config per domain.
    """
    
    # Application settings
    APP_NAME: str = "FA Application"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Database settings
    DATABASE_URL: str = "sqlite:///./fa_database.db"
    
    # File monitoring settings
    WATCH_PATH: Path = Path("./monitored_files")
    
    # Auth settings (delegated to auth_config)
    @property
    def SECRET_KEY(self) -> str:
        return auth_config.SECRET_KEY
    
    @property
    def ALGORITHM(self) -> str:
        return auth_config.ALGORITHM
    
    @property
    def ACCESS_TOKEN_EXPIRE_MINUTES(self) -> int:
        return auth_config.ACCESS_TOKEN_EXPIRE_MINUTES
    
    @property
    def REFRESH_TOKEN_EXPIRE_DAYS(self) -> int:
        return auth_config.REFRESH_TOKEN_EXPIRE_DAYS
    
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
        case_sensitive = True

settings = Settings()
