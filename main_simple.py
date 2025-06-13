"""
Simplified main application file for testing user management endpoints
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_application() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title="FA User Management API",
        description="User Management API with SOLID principles",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["*"],
    )
    
    # Include routers
    try:
        from app.api.v1.endpoints.users import router as users_router
        app.include_router(
            users_router,
            prefix="/api/v1/users",
            tags=["Users"]
        )
        logger.info("User management routes configured successfully")
    except ImportError as e:
        logger.warning(f"Could not import user routes: {e}")
    
    # Add health check endpoint
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Basic health check"""
        return {
            "status": "healthy",
            "service": "FA User Management API",
            "version": "1.0.0"
        }
    
    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint"""
        return {
            "message": "FA User Management API",
            "docs": "/docs",
            "health": "/health"
        }
    
    return app

# Create application instance
app = create_application()

if __name__ == "__main__":
    """Run application directly"""
    uvicorn.run(
        "main_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
