from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional

class AuthConfig(BaseSettings):
    """
    Konfigurasi khusus untuk domain authentication.
    Mengimplementasikan Single Responsibility Principle.
    """
    
    model_config = ConfigDict(
        env_file=".env",
        extra="ignore"  # Ignore extra fields from .env
    )
    
    # Security settings
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Password settings
    MIN_PASSWORD_LENGTH: int = 8
    REQUIRE_UPPERCASE: bool = True
    REQUIRE_LOWERCASE: bool = True
    REQUIRE_DIGITS: bool = True
    REQUIRE_SPECIAL_CHARS: bool = True
    
    # User settings
    MAX_LOGIN_ATTEMPTS: int = 5
    ACCOUNT_LOCKOUT_DURATION_MINUTES: int = 30
    
    # Registration settings
    ALLOW_REGISTRATION: bool = True
    REQUIRE_EMAIL_VERIFICATION: bool = False

auth_config = AuthConfig()
