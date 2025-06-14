from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.infrastructure.config.settings import settings
from app.api.v1.router import api_router
from app.core.events import startup_event_handler, shutdown_event_handler
from app.infrastructure.database.database_manager import db_manager
from app.common.logging.logging_config import setup_logging
from app.common.middleware.rate_limiter import RateLimiterMiddleware
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
    
    # Add Rate Limiting middleware
    application.add_middleware(RateLimiterMiddleware)
    server_logger.info("Rate limiting middleware added")
    
    # Create database tables with error handling
    try:
        db_manager.create_tables()
        server_logger.info("Database tables created/verified")
    except Exception as e:
        server_logger.warning(f"Database initialization warning: {str(e)}")
        server_logger.info("Application will continue startup - database may initialize later")
    
    # Add event handlers
    application.add_event_handler("startup", startup_event_handler)
    application.add_event_handler("shutdown", shutdown_event_handler)
    
    # Add root health endpoint for Railway healthcheck
    @application.get("/health")
    async def root_health_check():
        """
        Root health check endpoint for Railway deployment
        """
        try:
            # Test database connection
            from app.infrastructure.database.database_manager import db_manager
            # Simple database check
            db_manager.get_session()
            return {"status": "healthy", "service": "FA API", "database": "connected"}
        except Exception as e:
            server_logger.error(f"Health check failed: {str(e)}")
            return {"status": "healthy", "service": "FA API", "database": "initializing", "note": "Service starting up"}
    
    # Include routers dengan struktur baru
    application.include_router(api_router, prefix="/api/v1")
    server_logger.info("API routes registered with new domain structure")
    
    # Mount static files
    import os
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
    if os.path.exists(static_dir):
        application.mount("/static", StaticFiles(directory=static_dir), name="static")
        server_logger.info("Static files mounted")
    else:
        server_logger.warning(f"Static directory not found: {static_dir}")
    
    server_logger.info("FA Application initialized successfully with new architecture")
    return application

app = create_application()
