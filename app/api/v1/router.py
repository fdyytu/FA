from fastapi import APIRouter
from app.api.v1.endpoints import file_monitor

api_router = APIRouter()
api_router.include_router(file_monitor.router, prefix="/file-monitor", tags=["file-monitor"])