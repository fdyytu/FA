from fastapi import FastAPI
from app.infrastructure.config.settings import settings
from app.common.logging.logging_config import setup_logging
import logging

def create_base_application() -> FastAPI:
    """
    Factory function untuk membuat FastAPI application dasar.
    Hanya menangani inisialisasi dasar aplikasi.
    """
    
    # Setup logging terlebih dahulu
    setup_logging()
    
    # Get server logger
    server_logger = logging.getLogger('server')
    server_logger.info("Starting FA Application with new structure...")
    
    application = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG,
        version="2.0.0",
        description="FA API dengan arsitektur Domain-Driven Design, mengimplementasikan prinsip SOLID dan DRY"
    )
    
    server_logger.info("Base FA Application initialized")
    return application
