import logging
import os
from app.core.config import settings

def setup_logging():
    # Buat direktori logs jika belum ada
    os.makedirs('logs', exist_ok=True)
    
    # Setup formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOG_LEVEL)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # App log handler
    app_handler = logging.FileHandler('logs/app.log')
    app_handler.setFormatter(formatter)
    root_logger.addHandler(app_handler)
    
    # Server log handler untuk monitoring dan debug
    server_handler = logging.FileHandler('logs/server.log')
    server_handler.setFormatter(formatter)
    
    # Setup server logger khusus
    server_logger = logging.getLogger('server')
    server_logger.addHandler(server_handler)
    server_logger.setLevel(logging.INFO)
    
    # Setup PPOB logger khusus
    ppob_logger = logging.getLogger('ppob')
    ppob_handler = logging.FileHandler('logs/ppob.log')
    ppob_handler.setFormatter(formatter)
    ppob_logger.addHandler(ppob_handler)
    ppob_logger.setLevel(logging.INFO)
    
    # Setup admin logger khusus
    admin_logger = logging.getLogger('admin')
    admin_handler = logging.FileHandler('logs/admin.log')
    admin_handler.setFormatter(formatter)
    admin_logger.addHandler(admin_handler)
    admin_logger.setLevel(logging.INFO)
    
    # Log startup message
    server_logger.info("Logging system initialized")
    server_logger.info(f"Log level: {settings.LOG_LEVEL}")
