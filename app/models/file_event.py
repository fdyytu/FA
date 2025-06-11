from datetime import datetime
from pydantic import BaseModel
from pathlib import Path

class FileEvent(BaseModel):
    type: str
    path: str
    filename: str
    timestamp: datetime = datetime.utcnow()

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }