from app.infrastructure.application.app_factory import create_base_application
from app.infrastructure.application.middleware import setup_middleware
from app.infrastructure.application.health import setup_health_check
from app.infrastructure.application.static import setup_static_files
from app.api.v1.router import api_router
from app.core.events import startup_event_handler, shutdown_event_handler
from app.infrastructure.database.database_manager import db_manager
from app.common.logging.logging_config import setup_logging
import logging

def create_application():
    """
    Factory function untuk membuat FastAPI application dengan semua komponen.
    """
    # Setup logging system first
    setup_logging()
    
    server_logger = logging.getLogger('server')
    server_logger.info("🚀 Starting FA Application initialization...")
    
    # Buat aplikasi dasar
    application = create_base_application()
    server_logger.info("✅ Base application created")
    
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
    server_logger.info("✅ Static files setup completed")
    
    server_logger.info("🎯 FA Application initialization completed successfully!")
    server_logger.info("📊 Enhanced logging system active - All requests and errors will be logged")
    
    return application

app = create_application()
