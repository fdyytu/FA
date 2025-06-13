from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from enum import Enum

class DiscordBotStatusEnum(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    MAINTENANCE = "MAINTENANCE"

class CurrencyTypeEnum(str, Enum):
    WL = "wl"
    DL = "dl"
    BGL = "bgl"

# Discord Bot Schemas
class DiscordBotBase(BaseModel):
    bot_name: str = Field(..., max_length=100)
    guild_id: str = Field(..., max_length=50)
    live_stock_channel_id: Optional[str] = Field(None, max_length=50)
    donation_webhook_url: Optional[str] = None
    status: DiscordBotStatusEnum = DiscordBotStatusEnum.INACTIVE
    is_active: bool = True

class DiscordBotCreate(DiscordBotBase):
    bot_token: str = Field(..., description="Discord Bot Token")

class DiscordBotUpdate(BaseModel):
    bot_name: Optional[str] = Field(None, max_length=100)
    guild_id: Optional[str] = Field(None, max_length=50)
    live_stock_channel_id: Optional[str] = Field(None, max_length=50)
    donation_webhook_url: Optional[str] = None
    status: Optional[DiscordBotStatusEnum] = None
    is_active: Optional[bool] = None

class DiscordBotResponse(DiscordBotBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Discord Channel Schemas
class DiscordChannelBase(BaseModel):
    channel_id: str = Field(..., max_length=50)
    channel_name: str = Field(..., max_length=100)
    channel_type: str = Field(..., max_length=50)
    is_active: bool = True

class DiscordChannelCreate(DiscordChannelBase):
    bot_id: int

class DiscordChannelUpdate(BaseModel):
    channel_name: Optional[str] = Field(None, max_length=100)
    channel_type: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None

class DiscordChannelResponse(DiscordChannelBase):
    id: int
    bot_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Discord User Schemas
class DiscordUserBase(BaseModel):
    discord_id: str = Field(..., max_length=50)
    discord_username: str = Field(..., max_length=100)
    grow_id: Optional[str] = Field(None, max_length=100)
    is_verified: bool = False
    is_active: bool = True

class DiscordUserCreate(DiscordUserBase):
    pass

class DiscordUserUpdate(BaseModel):
    discord_username: Optional[str] = Field(None, max_length=100)
    grow_id: Optional[str] = Field(None, max_length=100)
    is_verified: Optional[bool] = None
    is_active: Optional[bool] = None

class DiscordUserResponse(DiscordUserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Discord Wallet Schemas
class DiscordWalletBase(BaseModel):
    wl_balance: Decimal = Field(default=Decimal("0"), ge=0)
    dl_balance: Decimal = Field(default=Decimal("0"), ge=0)
    bgl_balance: Decimal = Field(default=Decimal("0"), ge=0)

class DiscordWalletCreate(DiscordWalletBase):
    user_id: int

class DiscordWalletUpdate(BaseModel):
    wl_balance: Optional[Decimal] = Field(None, ge=0)
    dl_balance: Optional[Decimal] = Field(None, ge=0)
    bgl_balance: Optional[Decimal] = Field(None, ge=0)

class DiscordWalletResponse(DiscordWalletBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Discord Transaction Schemas
class DiscordTransactionBase(BaseModel):
    transaction_type: str = Field(..., max_length=50)
    currency_type: CurrencyTypeEnum
    amount: Decimal = Field(..., gt=0)
    description: Optional[str] = None
    reference_id: Optional[str] = Field(None, max_length=100)

class DiscordTransactionCreate(DiscordTransactionBase):
    user_id: int

class DiscordTransactionResponse(DiscordTransactionBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Live Stock Schemas
class LiveStockBase(BaseModel):
    product_code: str = Field(..., max_length=100)
    product_name: str = Field(..., max_length=200)
    price_wl: Decimal = Field(..., gt=0)
    stock_quantity: int = Field(default=0, ge=0)
    category: str = Field(..., max_length=100)
    description: Optional[str] = None
    is_featured: bool = False
    is_active: bool = True
    display_order: int = 0

class LiveStockCreate(LiveStockBase):
    bot_id: int

class LiveStockUpdate(BaseModel):
    product_name: Optional[str] = Field(None, max_length=200)
    price_wl: Optional[Decimal] = Field(None, gt=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    is_featured: Optional[bool] = None
    is_active: Optional[bool] = None
    display_order: Optional[int] = None

class LiveStockResponse(LiveStockBase):
    id: int
    bot_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Admin World Config Schemas
class AdminWorldConfigBase(BaseModel):
    world_name: str = Field(..., max_length=100)
    world_description: Optional[str] = None
    is_active: bool = True
    access_level: str = Field(default="public", max_length=50)

class AdminWorldConfigCreate(AdminWorldConfigBase):
    pass

class AdminWorldConfigUpdate(BaseModel):
    world_name: Optional[str] = Field(None, max_length=100)
    world_description: Optional[str] = None
    is_active: Optional[bool] = None
    access_level: Optional[str] = Field(None, max_length=50)

class AdminWorldConfigResponse(AdminWorldConfigBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Discord Bot Config Schemas
class DiscordBotConfigBase(BaseModel):
    config_key: str = Field(..., max_length=100)
    config_value: str
    config_type: str = Field(default="string", max_length=50)
    description: Optional[str] = None
    is_active: bool = True

class DiscordBotConfigCreate(DiscordBotConfigBase):
    pass

class DiscordBotConfigUpdate(BaseModel):
    config_value: Optional[str] = None
    config_type: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    is_active: Optional[bool] = None

class DiscordBotConfigResponse(DiscordBotConfigBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Currency Conversion Schemas
class CurrencyConversionRequest(BaseModel):
    from_currency: CurrencyTypeEnum
    to_currency: CurrencyTypeEnum
    amount: Decimal = Field(..., gt=0)

class CurrencyConversionResponse(BaseModel):
    from_currency: CurrencyTypeEnum
    to_currency: CurrencyTypeEnum
    original_amount: Decimal
    converted_amount: Decimal
    conversion_rate: Decimal

# Discord Bot Command Schemas
class BuyProductRequest(BaseModel):
    product_code: str
    quantity: int = Field(..., gt=0)
    payment_currency: CurrencyTypeEnum = CurrencyTypeEnum.WL

class BuyProductResponse(BaseModel):
    success: bool
    message: str
    transaction_id: Optional[int] = None
    remaining_balance: Optional[DiscordWalletResponse] = None

class BalanceResponse(BaseModel):
    discord_user: DiscordUserResponse
    wallet: DiscordWalletResponse
    total_wl_equivalent: Decimal

class WorldListResponse(BaseModel):
    worlds: List[AdminWorldConfigResponse]
    total_count: int
