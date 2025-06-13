import uvicorn
import os
from app.infrastructure.config.settings import settings

if __name__ == "__main__":
    # Gunakan PORT dari environment variable (Railway) atau default 8000 untuk development
    port = int(os.environ.get("PORT", 8000))
    
    # Konfigurasi untuk production deployment
    is_production = os.environ.get("RAILWAY_ENVIRONMENT") == "production" or not settings.DEBUG
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.DEBUG and not is_production,
        workers=1 if is_production else 1,
        timeout_keep_alive=120 if is_production else 5,
        access_log=True
    )
