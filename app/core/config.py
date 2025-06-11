from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    APP_NAME: str = "FileMonitor"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    WATCH_PATH: Path = Path("./monitored_files")
    
    class Config:
        env_file = ".env"

settings = Settings()