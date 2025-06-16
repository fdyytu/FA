from fastapi import APIRouter
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/health")
async def health_check():
    """
    Comprehensive health check endpoint
    """
    try:
        # Import dependencies inside function to avoid circular imports
        from app.core.database import engine
        from app.infrastructure.config.settings import settings
        from sqlalchemy import text, inspect
        
        # Check database connection
        db_status = await check_database_health()
        
        # Try to check Discord bot status (optional)
        discord_status = {"status": "not_configured", "healthy": True}
        try:
            from app.domains.discord.services.bot_manager import bot_manager
            bot_status = bot_manager.get_bot_status()
            discord_status = {
                "status": bot_status.get("status", "unknown"),
                "is_running": bot_status.get("is_running", False),
                "healthy": bot_manager.is_bot_healthy()
            }
        except Exception as discord_error:
            logger.warning(f"Discord bot status check failed: {discord_error}")
            discord_status = {"status": "error", "healthy": False, "error": str(discord_error)}
        
        # Determine overall health
        overall_healthy = (
            db_status.get("status") == "healthy" and 
            discord_status.get("healthy", True)
        )
        
        return {
            "status": "healthy" if overall_healthy else "degraded",
            "service": "FA API",
            "version": "1.0.0",
            "database": db_status,
            "discord_bot": discord_status,
            "timestamp": "2024-01-01T00:00:00Z"  # You can use datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in health check: {e}")
        return {
            "status": "error",
            "service": "FA API",
            "error": str(e),
            "timestamp": "2024-01-01T00:00:00Z"
        }

async def check_database_health():
    """Check database connection and return status"""
    try:
        from app.core.database import engine
        from app.infrastructure.config.settings import settings
        from sqlalchemy import text, inspect
        
        # Test database connection
        with engine.connect() as connection:
            # Simple query to test connection
            result = connection.execute(text("SELECT 1"))
            result.fetchone()
            
            # Get table count
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            return {
                "status": "healthy",
                "type": "PostgreSQL" if settings.is_postgresql else "SQLite",
                "url": settings.DATABASE_URL[:50] + "..." if len(settings.DATABASE_URL) > 50 else settings.DATABASE_URL,
                "tables_count": len(tables),
                "connection": "ok"
            }
            
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "connection": "failed"
        }
