"""
Schemas untuk domain game
"""
from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime

class GameCategoryBase(BaseModel):
    name: str
    code: str
    icon: Optional[str] = None
    is_active: bool = True

class GameCategoryCreate(GameCategoryBase):
    pass

class GameCategoryResponse(GameCategoryBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class GameProductBase(BaseModel):
    category_id: int
    name: str
    code: str
    price: float
    cost: float
    margin: float = 0.0
    stock: int = 0
    min_stock: int = 5
    is_active: bool = True
    description: Optional[str] = None
    validation_required: bool = True

class GameProductCreate(GameProductBase):
    pass

class GameProductResponse(GameProductBase):
    id: int
    created_at: datetime
    category: Optional[GameCategoryResponse] = None
    
    class Config:
        from_attributes = True

class GameValidationRequest(BaseModel):
    game_code: str
    user_id: str
    server_id: Optional[str] = None
    
    @validator('user_id')
    def validate_user_id(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('User ID tidak boleh kosong')
        return v.strip()

class GameValidationResponse(BaseModel):
    user_id: str
    server_id: Optional[str] = None
    nickname: Optional[str] = None
    is_valid: bool
    message: str
    
class GameTopupRequest(BaseModel):
    game_code: str
    user_id: str
    server_id: Optional[str] = None
    product_code: str
    discord_user_id: Optional[str] = None
