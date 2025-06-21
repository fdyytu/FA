from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.common.middleware.rate_limiter import RateLimiterMiddleware
from app.common.middleware.request_logger import RequestLoggingMiddleware, EndpointLoggingMiddleware
from app.common.middleware.error_handler import ErrorHandlerMiddleware
from app.infrastructure.config.settings import settings
import logging

def setup_middleware(app: FastAPI) -> None:
    """
    Setup semua middleware yang dibutuhkan aplikasi
    """
    server_logger = logging.getLogger('server')
    
    # Add Error Handler middleware (first to catch all errors)
    app.add_middleware(
        ErrorHandlerMiddleware,
        debug=settings.DEBUG
    )
    server_logger.info("✅ Error handler middleware added")
    
    # Add Request Logging middleware
    app.add_middleware(
        RequestLoggingMiddleware,
        log_body=settings.DEBUG,  # Only log body in debug mode
        log_headers=True
    )
    server_logger.info("✅ Request logging middleware added")
    
    # Add Endpoint Logging middleware
    app.add_middleware(EndpointLoggingMiddleware)
    server_logger.info("✅ Endpoint logging middleware added")
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Dalam production, ganti dengan domain yang spesifik
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    server_logger.info("✅ CORS middleware added")
    
    # Add Rate Limiting middleware
    app.add_middleware(RateLimiterMiddleware)
    server_logger.info("✅ Rate limiting middleware added")
    
    server_logger.info("🎯 All middleware setup completed")
