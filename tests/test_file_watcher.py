import pytest
from app.services.file_watcher import FileWatcherService
from pathlib import Path
import asyncio
import tempfile

@pytest.fixture
async def file_watcher():
    with tempfile.TemporaryDirectory() as tmpdir:
        service = FileWatcherService(Path(tmpdir))
        await service.start()
        yield service
        await service.stop()

@pytest.mark.asyncio
async def test_file_creation_detection(file_watcher):
    test_file = Path(file_watcher.watch_path) / "test.txt"
    test_file.write_text("test content")
    
    # Wait for event to be processed
    event = await asyncio.wait_for(file_watcher.event_queue.get(), timeout=1.0)
    
    assert event.type == "created"
    assert event.filename == "test.txt"
    assert Path(event.path).name == "test.txt"