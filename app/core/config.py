from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./ppob_api.db"
    DATABASE_TEST_URL: Optional[str] = None
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Application
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    ALLOWED_HOSTS: str = '["localhost", "127.0.0.1", "0.0.0.0"]'
    
    # External Services
    DIGIFLAZZ_USERNAME: str = ""
    DIGIFLAZZ_API_KEY: str = ""
    DIGIFLAZZ_BASE_URL: str = "https://api.digiflazz.com/v1"
    
    # Midtrans
    MIDTRANS_SERVER_KEY: str = ""
    MIDTRANS_CLIENT_KEY: str = ""
    MIDTRANS_IS_PRODUCTION: bool = False
    MIDTRANS_BASE_URL: str = "https://api.sandbox.midtrans.com/v2"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: str = "0"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    LOG_FILE: str = "logs/app.log"
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: str = "True"
    RATE_LIMIT_STORAGE: str = "memory"
    
    # Monitoring
    HEALTH_CHECK_ENABLED: str = "True"
    METRICS_ENABLED: str = "True"
    
    # CORS
    CORS_ORIGINS: str = '["http://localhost:3000", "http://localhost:8080"]'
    CORS_ALLOW_CREDENTIALS: str = "True"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Allow extra fields

# Create settings instance
settings = Settings()
