from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.infrastructure.config.settings import settings
from app.api.v1.new_router import api_router
from app.core.events import startup_event_handler, shutdown_event_handler
from app.infrastructure.database.database_manager import db_manager
from app.core.logging import setup_logging
import logging

def create_application() -> FastAPI:
    """
    Factory function untuk membuat FastAPI application.
    Mengimplementasikan Factory Pattern dan Dependency Injection.
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
    
    # Add CORS middleware
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Dalam production, ganti dengan domain yang spesifik
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Create database tables
    db_manager.create_tables()
    server_logger.info("Database tables created/verified")
    
    # Add event handlers
    application.add_event_handler("startup", startup_event_handler)
    application.add_event_handler("shutdown", shutdown_event_handler)
    
    # Include routers dengan struktur baru
    application.include_router(api_router, prefix="/api/v1")
    server_logger.info("API routes registered with new domain structure")
    
    # Mount static files
    application.mount("/static", StaticFiles(directory="static"), name="static")
    server_logger.info("Static files mounted")
    
    server_logger.info("FA Application initialized successfully with new architecture")
    return application

app = create_application()
