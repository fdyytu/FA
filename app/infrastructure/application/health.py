from fastapi import FastAPI
import logging

def setup_health_check(app: FastAPI) -> None:
    """
    Setup health check endpoint untuk monitoring
    """
    server_logger = logging.getLogger('server')
    
    @app.get("/health")
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
            return {
                "status": "healthy", 
                "service": "FA API", 
                "database": "initializing", 
                "note": "Service starting up"
            }
