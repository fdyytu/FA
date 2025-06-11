from fastapi import FastAPI
from app.core.config import Settings
from app.api.v1.router import api_router
from app.core.events import startup_event_handler, shutdown_event_handler

def create_application() -> FastAPI:
    settings = Settings()
    
    application = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG,
        version="1.0.0"
    )
    
    # Add event handlers
    application.add_event_handler("startup", startup_event_handler)
    application.add_event_handler("shutdown", shutdown_event_handler)
    
    # Include routers
    application.include_router(api_router, prefix="/api/v1")
    
    return application

app = create_application()