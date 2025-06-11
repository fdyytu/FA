from app.services.file_watcher import FileWatcherService
from app.core.config import settings
import logging

file_watcher_service = None

async def startup_event_handler():
    global file_watcher_service
    
    # Setup logging
    logging.basicConfig(level=settings.LOG_LEVEL)
    
    # Initialize file watcher service
    file_watcher_service = FileWatcherService(settings.WATCH_PATH)
    await file_watcher_service.start()

async def shutdown_event_handler():
    if file_watcher_service:
        await file_watcher_service.stop()