import pytest
from fastapi.testclient import TestClient
from app.main import app
from pathlib import Path
import tempfile
import shutil

@pytest.fixture
def test_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture
def client():
    return TestClient(app)

def test_file_creation_event(client, test_dir):
    test_file = test_dir / "test.txt"
    test_file.write_text("test content")
    
    response = client.get("/api/v1/file-monitor/events")
    assert response.status_code == 200
    events = response.json()
    
    assert len(events) > 0
    assert any(event["type"] == "created" and 
              event["filename"] == "test.txt" 
              for event in events)