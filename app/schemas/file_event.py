from pydantic import BaseModel
from datetime import datetime

class FileEventSchema(BaseModel):
    type: str
    path: str
    filename: str
    timestamp: datetime = datetime.utcnow()

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }