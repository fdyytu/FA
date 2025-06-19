from app.infrastructure.application.app_factory import create_base_application
from app.infrastructure.application.middleware import setup_middleware
from app.infrastructure.application.health import setup_health_check
from app.infrastructure.application.static import setup_static_files
from app.api.v1.router import api_router
from app.core.events import startup_event_handler, shutdown_event_handler
from app.infrastructure.database.database_manager import db_manager
import logging

def create_application():
    """
    Factory function untuk membuat FastAPI application dengan semua komponen.
    """
    server_logger = logging.getLogger('server')
    
    # Buat aplikasi dasar
    application = create_base_application()
    
    # Setup middleware
    setup_middleware(application)
    
    # Setup database
    try:
        db_manager.create_tables()
        server_logger.info("Database tables created/verified")
    except Exception as e:
        server_logger.warning(f"Database initialization warning: {str(e)}")
        server_logger.info("Application will continue startup - database may initialize later")
    
    # Setup event handlers
    application.add_event_handler("startup", startup_event_handler)
    application.add_event_handler("shutdown", shutdown_event_handler)
    
    # Setup health check endpoint
    setup_health_check(application)
    
    # Include API routes
    application.include_router(api_router, prefix="/api/v1")
    server_logger.info("API routes registered")
    
    # Setup static files
    setup_static_files(application)
    
    return application

app = create_application()
