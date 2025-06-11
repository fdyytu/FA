from fastapi import APIRouter, WebSocket, HTTPException
from app.services.file_watcher import file_watcher_service
from typing import List
from app.models.file_event import FileEvent

router = APIRouter()

@router.websocket("/ws/file-events")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            event = await file_watcher_service.event_queue.get()
            await websocket.send_json(event.dict())
    except Exception as e:
        await websocket.close()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/events", response_model=List[FileEvent])
async def get_events():
    """Get list of recent file events"""
    # Implementation for getting recent events
    pass