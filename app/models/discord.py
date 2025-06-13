from sqlalchemy import Column, String, Boolean, Text, Numeric, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum
from datetime import datetime

class DiscordBotStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"

class CurrencyType(enum.Enum):
    WL = "wl"
    DL = "dl"
    BGL = "bgl"

class DiscordBot(BaseModel):
    """Model untuk konfigurasi Discord Bot"""
    __tablename__ = "discord_bots"
    
    bot_name = Column(String(100), nullable=False)
    bot_token = Column(Text, nullable=False)  # Encrypted
    guild_id = Column(String(50), nullable=False)
    live_stock_channel_id = Column(String(50), nullable=True)
    donation_webhook_url = Column(Text, nullable=True)
    status = Column(Enum(DiscordBotStatus), default=DiscordBotStatus.INACTIVE)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    discord_channels = relationship("DiscordChannel", back_populates="bot")
    live_stocks = relationship("LiveStock", back_populates="bot")

class DiscordChannel(BaseModel):
    """Model untuk konfigurasi Discord Channel"""
    __tablename__ = "discord_channels"
    
    bot_id = Column(Integer, ForeignKey("discord_bots.id"), nullable=False)
    channel_id = Column(String(50), nullable=False)
    channel_name = Column(String(100), nullable=False)
    channel_type = Column(String(50), nullable=False)  # live_stock, donation, general
    is_active = Column(Boolean, default=True)
    
    # Relationships
    bot = relationship("DiscordBot", back_populates="discord_channels")

class DiscordUser(BaseModel):
    """Model untuk user Discord dengan Grow ID"""
    __tablename__ = "discord_users"
    
    discord_id = Column(String(50), unique=True, index=True, nullable=False)
    discord_username = Column(String(100), nullable=False)
    grow_id = Column(String(100), nullable=True)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    discord_wallet = relationship("DiscordWallet", back_populates="user", uselist=False)
    discord_transactions = relationship("DiscordTransaction", back_populates="user")

class DiscordWallet(BaseModel):
    """Model untuk wallet Discord dengan currency WL/DL/BGL"""
    __tablename__ = "discord_wallets"
    
    user_id = Column(Integer, ForeignKey("discord_users.id"), nullable=False)
    wl_balance = Column(Numeric(15, 2), default=0, nullable=False)  # World Lock
    dl_balance = Column(Numeric(15, 2), default=0, nullable=False)  # Diamond Lock (100 WL)
    bgl_balance = Column(Numeric(15, 2), default=0, nullable=False)  # Blue Gem Lock (100 DL)
    
    # Relationships
    user = relationship("DiscordUser", back_populates="discord_wallet")

class DiscordTransaction(BaseModel):
    """Model untuk transaksi Discord"""
    __tablename__ = "discord_transactions"
    
    user_id = Column(Integer, ForeignKey("discord_users.id"), nullable=False)
    transaction_type = Column(String(50), nullable=False)  # buy, deposit, withdraw, convert
    currency_type = Column(Enum(CurrencyType), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    description = Column(Text, nullable=True)
    reference_id = Column(String(100), nullable=True)  # untuk referensi ke transaksi lain
    
    # Relationships
    user = relationship("DiscordUser", back_populates="discord_transactions")

class LiveStock(BaseModel):
    """Model untuk produk yang ditampilkan di live stock Discord"""
    __tablename__ = "live_stocks"
    
    bot_id = Column(Integer, ForeignKey("discord_bots.id"), nullable=False)
    product_code = Column(String(100), nullable=False)
    product_name = Column(String(200), nullable=False)
    price_wl = Column(Numeric(15, 2), nullable=False)  # Harga dalam WL
    stock_quantity = Column(Integer, default=0, nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_featured = Column(Boolean, default=False)  # Untuk highlight produk
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)  # Untuk urutan tampilan
    
    # Relationships
    bot = relationship("DiscordBot", back_populates="live_stocks")

class AdminWorldConfig(BaseModel):
    """Model untuk konfigurasi world admin"""
    __tablename__ = "admin_world_configs"
    
    world_name = Column(String(100), nullable=False)
    world_description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    access_level = Column(String(50), default="public")  # public, vip, admin
    
class DiscordBotConfig(BaseModel):
    """Model untuk konfigurasi tambahan Discord Bot"""
    __tablename__ = "discord_bot_configs"
    
    config_key = Column(String(100), unique=True, index=True, nullable=False)
    config_value = Column(Text, nullable=False)
    config_type = Column(String(50), default="string")  # string, number, boolean, json
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
