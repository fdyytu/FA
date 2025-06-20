from sqlalchemy import Column, String, Boolean, Text, Numeric
from sqlalchemy.orm import relationship
from app.common.base_classes.base import BaseModel

class User(BaseModel):
    """
    User model - Single Responsibility: Mengelola data user
    """
    __tablename__ = "users"
    
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    hashed_password = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    phone_number = Column(String(20), nullable=True)
    balance = Column(Numeric(15, 2), default=0, nullable=False)
    
    # Relationships
    ppob_transactions = relationship("PPOBTransaction", back_populates="user")
