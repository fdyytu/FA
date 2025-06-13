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
    APP_NAME: str = "Discord Bot Admin Dashboard"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    ALLOWED_HOSTS: str = '["localhost", "127.0.0.1", "0.0.0.0"]'
    WATCH_PATH: str = "/tmp/watch"
    
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
    
    # Cache Settings
    CACHE_ENABLED: bool = True
    CACHE_DEFAULT_TTL: int = 1800  # 30 menit dalam detik
    CACHE_REDIS_TTL: int = 3600    # 1 jam untuk Redis
    CACHE_MEMORY_TTL: int = 900    # 15 menit untuk Memory
    CACHE_MAX_MEMORY_SIZE: int = 1000  # Max items di memory cache
    
    # Cache per Domain
    CACHE_PPOB_PRODUCT_TTL: int = 3600     # 1 jam untuk PPOB products
    CACHE_PPOB_INQUIRY_TTL: int = 300      # 5 menit untuk inquiry
    CACHE_USER_PROFILE_TTL: int = 1800     # 30 menit untuk user profile
    CACHE_TRANSACTION_TTL: int = 600       # 10 menit untuk transaction
    
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
