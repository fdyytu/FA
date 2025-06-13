import uvicorn
import os
from app.infrastructure.config.settings import settings

if __name__ == "__main__":
    # Gunakan PORT dari environment variable (Railway) atau default 8000 untuk development
    port = int(os.environ.get("PORT", 8000))
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.DEBUG
    )
