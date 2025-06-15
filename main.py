from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.v1.router import api_router
import logging
import os

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

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include API router
app.include_router(api_router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    """Startup event - Initialize and start Discord bot"""
    try:
        from app.domains.discord.services.bot_manager import bot_manager
        
        logger.info("Starting FA API Service...")
        
        # Initialize Discord bot (try database first, then environment)
        logger.info("Initializing Discord bot...")
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
        
        bot_status = bot_manager.get_bot_status()
        
        return {
            "status": "healthy", 
            "service": "FA API",
            "discord_bot": {
                "status": bot_status.get("status", "unknown"),
                "is_running": bot_status.get("is_running", False),
                "healthy": bot_manager.is_bot_healthy()
            }
        }
    except Exception as e:
        logger.error(f"Error in health check: {e}")
        return {
            "status": "healthy", 
            "service": "FA API",
            "discord_bot": {
                "status": "error",
                "error": str(e)
            }
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
