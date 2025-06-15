from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.v1.router import api_router
from app.common.middleware.rate_limiter import RateLimiterMiddleware
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import models to register them with SQLAlchemy Base
try:
    from app.domains.discord.models.discord_config import DiscordConfig
except ImportError:
    pass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="FA API Service",
    description="FastAPI application with Analytics and Product domains + Discord Bot",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Rate Limiter middleware
app.add_middleware(RateLimiterMiddleware)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include API router
app.include_router(api_router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    """Startup event - Initialize database and start Discord bot"""
    try:
        logger.info("Starting FA API Service...")
        
        # Auto-create database tables
        logger.info("Initializing database tables...")
        await auto_create_database_tables()
        
        # Initialize Discord bot (try database first, then environment)
        logger.info("Initializing Discord bot...")
        from app.domains.discord.services.bot_manager import bot_manager
        success = await bot_manager.auto_initialize()
        
        if success:
            logger.info("Starting Discord bot...")
            await bot_manager.start_bot()
            logger.info(f"Discord bot started successfully from {bot_manager.config_source}")
        else:
            logger.warning("Failed to initialize Discord bot - no valid configuration found in database or environment")
            
        logger.info("FA API Service startup completed")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")

async def auto_create_database_tables():
    """Auto-create database tables if they don't exist"""
    try:
        from app.core.database import engine, Base
        from app.infrastructure.config.settings import settings
        
        # Import all models to register them with SQLAlchemy
        logger.info("Importing database models...")
        
        # Import models (ignore import errors for missing models)
        models_imported = []
        
        try:
            from app.domains.discord.models.discord_config import DiscordConfig
            models_imported.append("DiscordConfig")
        except ImportError:
            pass
            
        try:
            from app.domains.wallet.models.wallet import Wallet
            models_imported.append("Wallet")
        except ImportError:
            pass
            
        try:
            from app.domains.admin.models.admin import Admin
            models_imported.append("Admin")
        except ImportError:
            pass
            
        try:
            from app.domains.product.models.product import Product
            models_imported.append("Product")
        except ImportError:
            pass
            
        try:
            from app.domains.auth.models.user import User
            models_imported.append("User")
        except ImportError:
            pass
            
        try:
            from app.domains.voucher.models.voucher import Voucher
            models_imported.append("Voucher")
        except ImportError:
            pass
            
        try:
            from app.domains.analytics.models.analytics import Analytics
            models_imported.append("Analytics")
        except ImportError:
            pass
        
        logger.info(f"Models imported: {models_imported}")
        
        # Create all tables
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        
        # Verify tables created
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if settings.is_postgresql:
            logger.info(f"PostgreSQL tables created: {len(tables)} tables")
        else:
            logger.info(f"SQLite tables created: {len(tables)} tables")
            
        for table in tables:
            logger.debug(f"  - {table}")
            
        logger.info("Database initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
        # Don't raise exception to allow app to continue running

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event - Stop Discord bot gracefully"""
    try:
        from app.domains.discord.services.bot_manager import bot_manager
        
        logger.info("Shutting down FA API Service...")
        
        # Stop Discord bot
        if bot_manager.is_initialized:
            logger.info("Stopping Discord bot...")
            await bot_manager.stop_bot()
            logger.info("Discord bot stopped")
            
        logger.info("FA API Service shutdown completed")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "FA API Service is running",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "discord_dashboard": "/static/discord-dashboard.html"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        from app.domains.discord.services.bot_manager import bot_manager
        from app.core.database import engine
        from app.infrastructure.config.settings import settings
        from sqlalchemy import text, inspect
        
        # Check database connection
        db_status = await check_database_health()
        
        # Check Discord bot
        bot_status = bot_manager.get_bot_status()
        
        return {
            "status": "healthy", 
            "service": "FA API",
            "database": db_status,
            "discord_bot": {
                "status": bot_status.get("status", "unknown"),
                "is_running": bot_status.get("is_running", False),
                "healthy": bot_manager.is_bot_healthy()
            }
        }
    except Exception as e:
        logger.error(f"Error in health check: {e}")
        return {
            "status": "error", 
            "service": "FA API",
            "error": str(e)
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
