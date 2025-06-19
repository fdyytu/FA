from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.common.middleware.rate_limiter import RateLimiterMiddleware
import logging

def setup_middleware(app: FastAPI) -> None:
    """
    Setup semua middleware yang dibutuhkan aplikasi
    """
    server_logger = logging.getLogger('server')
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Dalam production, ganti dengan domain yang spesifik
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add Rate Limiting middleware
    app.add_middleware(RateLimiterMiddleware)
    server_logger.info("Middleware setup completed")
