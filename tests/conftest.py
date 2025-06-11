import pytest
from app.main import app
from fastapi.testclient import TestClient
import asyncio

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()