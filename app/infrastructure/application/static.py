from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
import logging

def setup_static_files(app: FastAPI) -> None:
    """
    Setup static files mounting untuk aplikasi
    """
    server_logger = logging.getLogger('server')
    
    # Mount static files - path ke root directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))))
    static_dir = os.path.join(project_root, "workspace", "static")
    
    # Alternative path jika yang pertama tidak ada
    if not os.path.exists(static_dir):
        static_dir = os.path.join(os.getcwd(), "static")
    
    if os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
        server_logger.info(f"Static files mounted from: {static_dir}")
    else:
        server_logger.warning(f"Static directory not found: {static_dir}")
        server_logger.info(f"Current working directory: {os.getcwd()}")
