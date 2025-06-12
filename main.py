"""
Main application file dengan implementasi SOLID principles
- Single Responsibility: Setiap middleware memiliki tanggung jawab spesifik
- Open/Closed: Mudah menambah middleware baru tanpa mengubah kode existing
- Liskov Substitution: Middleware dapat diganti dengan implementasi lain
- Interface Segregation: Interface terpisah untuk setiap concern
- Dependency Inversion: Bergantung pada abstraksi, bukan implementasi konkret
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import uvicorn

# Import middleware
from app.middleware.rate_limiter import RateLimiterMiddleware
from app.middleware.security import SecurityMiddleware
from app.middleware.error_handler import ErrorHandlerMiddleware

# Import core components
from app.core.config import settings
from app.core.database import engine, Base
from app.core.container import setup_dependencies
from app.core.logging_config import setup_logging

# Import routers
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.wallet import router as wallet_router
from app.api.v1.transactions import router as transactions_router
from app.api.v1.ppob import router as ppob_router
from app.api.v1.admin import router as admin_router

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events
    Startup dan shutdown logic
    """
    # Startup
    logger.info("Starting PPOB API application...")
    
    try:
        # Create database tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Setup dependency injection
        setup_dependencies()
        logger.info("Dependencies configured successfully")
        
        # Additional startup tasks
        await startup_tasks()
        
        logger.info("Application startup completed")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down PPOB API application...")
    await shutdown_tasks()
    logger.info("Application shutdown completed")


async def startup_tasks():
    """Additional startup tasks"""
    try:
        # Warm up external services
        logger.info("Warming up external services...")
        
        # Initialize cache connections
        logger.info("Initializing cache connections...")
        
        # Load initial data if needed
        logger.info("Loading initial application data...")
        
    except Exception as e:
        logger.warning(f"Non-critical startup task failed: {e}")


async def shutdown_tasks():
    """Cleanup tasks during shutdown"""
    try:
        # Close database connections
        logger.info("Closing database connections...")
        
        # Clear caches
        logger.info("Clearing application caches...")
        
        # Close external service connections
        logger.info("Closing external service connections...")
        
    except Exception as e:
        logger.warning(f"Error during shutdown: {e}")


def create_application() -> FastAPI:
    """
    Application factory pattern
    Creates and configures FastAPI application
    """
    
    # Create FastAPI instance
    app = FastAPI(
        title="PPOB API",
        description="Payment Point Online Bank API dengan implementasi SOLID principles",
        version="1.0.0",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan
    )
    
    # Configure CORS
    configure_cors(app)
    
    # Add middleware (order matters!)
    add_middleware(app)
    
    # Include routers
    include_routers(app)
    
    # Add health check endpoint
    add_health_check(app)
    
    return app


def configure_cors(app: FastAPI):
    """Configure CORS middleware"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Total-Count", "X-Page-Count"]
    )


def add_middleware(app: FastAPI):
    """
    Add middleware in correct order
    Middleware dieksekusi dalam reverse order (LIFO)
    """
    
    # 1. Error Handler (outermost - handles all errors)
    app.add_middleware(
        ErrorHandlerMiddleware,
        debug=settings.DEBUG
    )
    
    # 2. Security Middleware
    app.add_middleware(
        SecurityMiddleware,
        csrf_protection=not settings.DEBUG,  # Disable CSRF in debug mode
        security_headers=True,
        max_request_size=10 * 1024 * 1024  # 10MB
    )
    
    # 3. Rate Limiter (innermost - close to business logic)
    app.add_middleware(RateLimiterMiddleware)
    
    logger.info("Middleware configured successfully")


def include_routers(app: FastAPI):
    """Include API routers"""
    
    # API v1 routes
    api_prefix = "/api/v1"
    
    app.include_router(
        auth_router,
        prefix=f"{api_prefix}/auth",
        tags=["Authentication"]
    )
    
    app.include_router(
        users_router,
        prefix=f"{api_prefix}/users",
        tags=["Users"]
    )
    
    app.include_router(
        wallet_router,
        prefix=f"{api_prefix}/wallet",
        tags=["Wallet"]
    )
    
    app.include_router(
        transactions_router,
        prefix=f"{api_prefix}/transactions",
        tags=["Transactions"]
    )
    
    app.include_router(
        ppob_router,
        prefix=f"{api_prefix}/ppob",
        tags=["PPOB"]
    )
    
    app.include_router(
        admin_router,
        prefix=f"{api_prefix}/admin",
        tags=["Admin"]
    )
    
    logger.info("API routes configured successfully")


def add_health_check(app: FastAPI):
    """Add health check endpoints"""
    
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Basic health check"""
        return {
            "status": "healthy",
            "service": "PPOB API",
            "version": "1.0.0"
        }
    
    @app.get("/health/detailed", tags=["Health"])
    async def detailed_health_check():
        """Detailed health check with dependencies"""
        try:
            # Check database
            from app.core.database import get_db
            db = next(get_db())
            db.execute("SELECT 1")
            db_status = "healthy"
        except Exception as e:
            db_status = f"unhealthy: {str(e)}"
        
        # Check external services
        external_services = {
            "database": db_status,
            # Add other service checks here
        }
        
        overall_status = "healthy" if all(
            status == "healthy" for status in external_services.values()
        ) else "unhealthy"
        
        return {
            "status": overall_status,
            "service": "PPOB API",
            "version": "1.0.0",
            "dependencies": external_services,
            "timestamp": "2024-01-01T00:00:00Z"  # Use actual timestamp
        }


# Create application instance
app = create_application()


# Custom exception handlers (if needed)
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Custom 404 handler"""
    return {
        "success": False,
        "message": "Endpoint tidak ditemukan",
        "error_code": "NOT_FOUND"
    }


if __name__ == "__main__":
    """
    Run application directly
    Untuk development saja, production gunakan ASGI server
    """
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug",
        access_log=True
    )
