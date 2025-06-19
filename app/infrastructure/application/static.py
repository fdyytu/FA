from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
import logging

def setup_static_files(app: FastAPI) -> None:
    """
    Setup static files mounting untuk aplikasi
    """
    server_logger = logging.getLogger('server')
    
    # Mount static files
    static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "static")
    if os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
        server_logger.info("Static files mounted")
    else:
        server_logger.warning(f"Static directory not found: {static_dir}")
