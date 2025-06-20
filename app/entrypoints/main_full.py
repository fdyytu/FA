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
        
        # Discord models
        try:
            from app.domains.discord.models.discord_config import DiscordConfig
            models_imported.append("DiscordConfig")
        except ImportError:
            pass
            
        # Wallet models - perbaiki import yang salah
        try:
            from app.domains.wallet.models.wallet import WalletTransaction, Transfer, TopUpRequest
            models_imported.extend(["WalletTransaction", "Transfer", "TopUpRequest"])
        except ImportError:
            pass
            
        # Admin models - import semua model admin
        try:
            from app.domains.admin.models.admin import Admin, AdminConfig, PPOBMarginConfig, AdminAuditLog, AdminNotificationSetting
            models_imported.extend(["Admin", "AdminConfig", "PPOBMarginConfig", "AdminAuditLog", "AdminNotificationSetting"])
        except ImportError:
            pass
            
        # Product models
        try:
            from app.domains.product.models.product import Product
            models_imported.append("Product")
        except ImportError:
            pass
            
        # Auth/User models
        try:
            from app.domains.auth.models.user import User
            models_imported.append("User")
        except ImportError:
            pass
            
        # Voucher models - import semua model voucher
        try:
            from app.domains.voucher.models.voucher import Voucher, VoucherUsage
            models_imported.extend(["Voucher", "VoucherUsage"])
        except ImportError:
            pass
            
        # Analytics models - import semua model analytics
        try:
            from app.domains.analytics.models.analytics import AnalyticsEvent, ProductAnalytics, VoucherAnalytics, DashboardMetrics
            models_imported.extend(["AnalyticsEvent", "ProductAnalytics", "VoucherAnalytics", "DashboardMetrics"])
        except ImportError:
            pass
            
        # PPOB models - tambahkan model PPOB yang hilang
        try:
            from app.domains.ppob.models.ppob import PPOBTransaction, PPOBProduct
            models_imported.extend(["PPOBTransaction", "PPOBProduct"])
        except ImportError:
            pass
            
        # Transaction models - import model transaction yang baru
        try:
            from app.domains.transaction.models.transaction import Transaction, TransactionLog
            models_imported.extend(["Transaction", "TransactionLog"])
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
async def health_check_root():
    """Simple health check endpoint for monitoring systems"""
    try:
        # Simple database check
        db_status = await check_database_health()
        
        return {
            "status": "healthy" if db_status.get("status") == "healthy" else "unhealthy",
            "service": "FA API",
            "database": db_status.get("status", "unknown")
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "unhealthy",
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
