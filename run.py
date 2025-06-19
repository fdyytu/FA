"""
Entry point untuk Railway deployment
File ini dibuat untuk mengatasi error: python: can't open file '/app/run.py'
"""
import os
import sys
import logging
from app.main import app

# Setup logging untuk debugging deployment
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """
    Main function untuk menjalankan aplikasi di Railway
    """
    try:
        import uvicorn
        
        # Ambil PORT dari environment variable Railway
        port = int(os.environ.get("PORT", 8000))
        host = "0.0.0.0"
        
        logger.info(f"Starting FA Application on {host}:{port}")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Working directory: {os.getcwd()}")
        
        # Jalankan aplikasi dengan uvicorn
        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=False,
            workers=1,
            log_level="info"
        )
        
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
