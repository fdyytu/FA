from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
import asyncio
from typing import Optional, Union
import logging
from app.domains.file_monitor.models.file_event import FileEvent
from app.infrastructure.config.settings import settings

logger = logging.getLogger(__name__)

class FileEventHandler(FileSystemEventHandler):
    def __init__(self):
        self.event_queue = asyncio.Queue()

    async def process_file_event(self, event_type: str, file_path: str):
        event = FileEvent(
            type=event_type,
            path=file_path,
            filename=Path(file_path).name
        )
        await self.event_queue.put(event)
        logger.info(f"File event detected: {event_type} - {file_path}")

    def on_created(self, event):
        if not event.is_directory:
            asyncio.create_task(self.process_file_event("created", event.src_path))

    def on_modified(self, event):
        if not event.is_directory:
            asyncio.create_task(self.process_file_event("modified", event.src_path))

    def on_deleted(self, event):
        if not event.is_directory:
            asyncio.create_task(self.process_file_event("deleted", event.src_path))

class FileWatcherService:
    def __init__(self, watch_path: Union[str, Path]):
        self.watch_path = Path(watch_path) if isinstance(watch_path, str) else watch_path
        self.observer: Optional[Observer] = None
        self.event_handler = FileEventHandler()

    async def start(self):
        self.watch_path.mkdir(parents=True, exist_ok=True)
        
        self.observer = Observer()
        self.observer.schedule(
            self.event_handler,
            str(self.watch_path),
            recursive=True
        )
        self.observer.start()
        logger.info(f"Started watching directory: {self.watch_path}")

    async def stop(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()
            logger.info("Stopped file watching service")

    @property
    def event_queue(self):
        return self.event_handler.event_queue
