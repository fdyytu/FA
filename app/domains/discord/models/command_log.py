from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.sql import func
from app.core.database import Base

class DiscordCommandLog(Base):
    __tablename__ = "discord_command_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), nullable=False, index=True)
    username = Column(String(100), nullable=False)
    channel_id = Column(String(50), nullable=False, index=True)
    channel_name = Column(String(100))
    guild_id = Column(String(50), index=True)
    guild_name = Column(String(100))
    
    command = Column(String(200), nullable=False, index=True)
    command_args = Column(Text)
    response_status = Column(String(20), default="success")
    response_message = Column(Text)
    
    execution_time_ms = Column(Integer, default=0)
    error_message = Column(Text)
    is_successful = Column(Boolean, default=True)
    
    timestamp = Column(DateTime(timezone=True), 
                      server_default=func.now(), index=True)
    
    def __repr__(self):
        return f"<DiscordCommandLog(id={self.id}, user={self.username}, command={self.command})>"
    
    @property
    def formatted_timestamp(self):
        return self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.username,
            "channel_id": self.channel_id,
            "channel_name": self.channel_name,
            "guild_id": self.guild_id,
            "guild_name": self.guild_name,
            "command": self.command,
            "command_args": self.command_args,
            "response_status": self.response_status,
            "response_message": self.response_message,
            "execution_time_ms": self.execution_time_ms,
            "error_message": self.error_message,
            "is_successful": self.is_successful,
            "timestamp": self.formatted_timestamp
        }
