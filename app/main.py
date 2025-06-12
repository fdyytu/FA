from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import Settings
from app.api.v1.router import api_router
from app.core.events import startup_event_handler, shutdown_event_handler
from app.core.database import engine
from app.core.logging import setup_logging
from app.models import Base
import logging

def create_application() -> FastAPI:
    settings = Settings()
    
    # Setup logging terlebih dahulu
    setup_logging()
    
    # Get server logger
    server_logger = logging.getLogger('server')
    server_logger.info("Starting FA Application...")
    
    application = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG,
        version="1.0.0",
        description="FA API dengan fitur Authentication, PPOB, dan Admin Dashboard"
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
    Base.metadata.create_all(bind=engine)
    server_logger.info("Database tables created/verified")
    
    # Add event handlers
    application.add_event_handler("startup", startup_event_handler)
    application.add_event_handler("shutdown", shutdown_event_handler)
    
    # Include routers
    application.include_router(api_router, prefix="/api/v1")
    server_logger.info("API routes registered")
    
    server_logger.info("FA Application initialized successfully")
    return application

app = create_application()
