from typing import Generator
from app.services.file_watcher import FileWatcherService
from app.core.config import settings

def get_file_watcher() -> Generator[FileWatcherService, None, None]:
    try:
        service = FileWatcherService(settings.WATCH_PATH)
        yield service
    finally:
        service.stop()