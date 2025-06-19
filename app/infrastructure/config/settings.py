from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional
from pathlib import Path
from app.infrastructure.config.auth_config import auth_config

class Settings(BaseSettings):
    """
    Main application settings yang mengintegrasikan semua domain configs.
    Mengimplementasikan Single Responsibility Principle dengan memisahkan config per domain.
    """
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"  # Ignore extra fields from .env
    )
    
    # Application settings
    APP_NAME: str = "FA Application"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Database settings - Railway akan provide PostgreSQL URL otomatis
    DATABASE_URL: str = "sqlite:///./fa_database.db"  # Fallback untuk development
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Override DATABASE_URL from environment if available
        import os
        env_db_url = os.getenv('DATABASE_URL')
        if env_db_url:
            self.DATABASE_URL = env_db_url
            # Fix postgres:// to postgresql:// for SQLAlchemy compatibility
            if self.DATABASE_URL.startswith('postgres://'):
                self.DATABASE_URL = self.DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    # PostgreSQL specific settings
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600
    
    @property
    def is_postgresql(self) -> bool:
        """Check if using PostgreSQL database"""
        return "postgresql" in self.DATABASE_URL
    
    @property
    def is_sqlite(self) -> bool:
        """Check if using SQLite database"""
        return "sqlite" in self.DATABASE_URL
    
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
    
    # Redis settings (optional - untuk caching)
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: str = "0"

settings = Settings()
