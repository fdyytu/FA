"""
Entry point utama untuk FA Application
Menggunakan factory pattern dari app/main.py
"""
from app.main import app

if __name__ == "__main__":
    import uvicorn
    import os
    
    # Gunakan PORT dari environment variable atau default 8000
    port = int(os.environ.get("PORT", 8000))
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        reload=False
    )
