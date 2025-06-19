from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.domains.analytics.controllers.analytics_controller import router as analytics_router
from app.domains.product.controllers.product_controller import router as product_router
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="FA API Service - Analytics & Product",
    description="FastAPI application with Analytics and Product domains",
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

# Include only Analytics and Product routers
app.include_router(analytics_router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(product_router, prefix="/api/v1/products", tags=["products"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "FA API Service - Analytics & Product domains",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "available_endpoints": {
            "analytics": "/api/v1/analytics",
            "products": "/api/v1/products"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "FA API - Analytics & Product"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
