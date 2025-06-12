from fastapi import APIRouter, WebSocket, HTTPException, Depends
from app.services.file_watcher import FileWatcherService
from app.api.deps import get_file_watcher
from typing import List
from app.models.file_event import FileEvent

router = APIRouter()

@router.websocket("/ws/file-events")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        # Create a file watcher instance for this websocket connection
        from app.core.config import settings
        file_watcher = FileWatcherService(settings.WATCH_PATH)
        await file_watcher.start()
        
        while True:
            event = await file_watcher.event_queue.get()
            await websocket.send_json({
                "type": event.type,
                "path": event.path,
                "filename": event.filename,
                "timestamp": event.timestamp.isoformat() if event.timestamp else None
            })
    except Exception as e:
        await websocket.close()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/events")
async def get_events():
    """Get list of recent file events"""
    return {"message": "File monitoring is active", "status": "running"}
