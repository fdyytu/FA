from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.common.base_classes.base import Base

class FileEvent(Base):
    __tablename__ = "file_events"
    
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(50), nullable=False)  # created, modified, deleted, moved
    path = Column(Text, nullable=False)
    filename = Column(String(255), nullable=False)
    size = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<FileEvent(id={self.id}, type={self.type}, filename={self.filename})>"
