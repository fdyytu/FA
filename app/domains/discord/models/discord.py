"""
Discord Models
Model untuk Discord Bot, Users, Logs, dan Commands
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import ENUM
from app.core.database import Base


class DiscordBot(Base):
    """Model untuk Discord Bot"""
    __tablename__ = "discord_bots"
    
    id = Column(Integer, primary_key=True, index=True)
    bot_name = Column(String(100), nullable=False)
    bot_token = Column(Text, nullable=False)
    guild_id = Column(String(50), nullable=False, unique=True, index=True)
    live_stock_channel_id = Column(String(50), nullable=True)
    donation_webhook_url = Column(Text, nullable=True)
    status = Column(ENUM('ACTIVE', 'INACTIVE', 'MAINTENANCE', name='discordbotstatus'), 
                   nullable=False, default='INACTIVE')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    channels = relationship("DiscordChannel", back_populates="bot", cascade="all, delete-orphan")
    live_stocks = relationship("LiveStock", back_populates="bot", cascade="all, delete-orphan")


class DiscordChannel(Base):
    """Model untuk Discord Channel"""
    __tablename__ = "discord_channels"
    
    id = Column(Integer, primary_key=True, index=True)
    bot_id = Column(Integer, ForeignKey("discord_bots.id", ondelete="CASCADE"), nullable=False)
    channel_id = Column(String(50), nullable=False)
    channel_name = Column(String(100), nullable=False)
    channel_type = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    bot = relationship("DiscordBot", back_populates="channels")


class DiscordUser(Base):
    """Model untuk Discord User"""
    __tablename__ = "discord_users"
    
    id = Column(Integer, primary_key=True, index=True)
    discord_id = Column(String(50), nullable=False, unique=True, index=True)
    discord_username = Column(String(100), nullable=False)
    grow_id = Column(String(100), nullable=True)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    discord_wallet = relationship("DiscordWallet", back_populates="user", uselist=False)
    transactions = relationship("DiscordTransaction", back_populates="user")
    logs = relationship("DiscordLog", back_populates="user")
    commands = relationship("DiscordCommand", back_populates="user")


class DiscordWallet(Base):
    """Model untuk Discord Wallet"""
    __tablename__ = "discord_wallets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("discord_users.id", ondelete="CASCADE"), 
                    nullable=False, unique=True, index=True)
    wl_balance = Column(Numeric(15, 2), default=0)
    dl_balance = Column(Numeric(15, 2), default=0)
    bgl_balance = Column(Numeric(15, 2), default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("DiscordUser", back_populates="discord_wallet")


class DiscordTransaction(Base):
    """Model untuk Discord Transaction"""
    __tablename__ = "discord_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("discord_users.id", ondelete="CASCADE"), nullable=False)
    transaction_type = Column(String(50), nullable=False)  # 'purchase', 'deposit', 'withdraw'
    amount = Column(Numeric(15, 2), nullable=False)
    currency_type = Column(ENUM('wl', 'dl', 'bgl', name='currencytype'), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), default='completed')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("DiscordUser", back_populates="transactions")


class LiveStock(Base):
    """Model untuk Live Stock Products"""
    __tablename__ = "live_stocks"
    
    id = Column(Integer, primary_key=True, index=True)
    bot_id = Column(Integer, ForeignKey("discord_bots.id", ondelete="CASCADE"), nullable=False)
    product_code = Column(String(100), nullable=False, index=True)
    product_name = Column(String(200), nullable=False)
    price_wl = Column(Numeric(15, 2), nullable=False)
    stock_quantity = Column(Integer, default=0)
    category = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_featured = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    bot = relationship("DiscordBot", back_populates="live_stocks")


class AdminWorldConfig(Base):
    """Model untuk Admin World Configuration"""
    __tablename__ = "admin_world_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    world_name = Column(String(100), nullable=False)
    world_description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    access_level = Column(String(50), default='public')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DiscordBotConfig(Base):
    """Model untuk Discord Bot Configuration"""
    __tablename__ = "discord_bot_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    config_key = Column(String(100), nullable=False, unique=True, index=True)
    config_value = Column(Text, nullable=False)
    config_type = Column(String(50), default='string')
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DiscordLog(Base):
    """Model untuk Discord Bot Logs"""
    __tablename__ = "discord_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("discord_users.id", ondelete="SET NULL"), nullable=True)
    bot_id = Column(Integer, ForeignKey("discord_bots.id", ondelete="CASCADE"), nullable=True)
    level = Column(String(20), nullable=False, default='INFO')  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    message = Column(Text, nullable=False)
    action = Column(String(100), nullable=True)  # command, event, error, etc.
    channel_id = Column(String(50), nullable=True)
    guild_id = Column(String(50), nullable=True)
    error_details = Column(Text, nullable=True)
    extra_data = Column(Text, nullable=True)  # JSON string for additional data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("DiscordUser", back_populates="logs")


class DiscordCommand(Base):
    """Model untuk Discord Commands History"""
    __tablename__ = "discord_commands"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("discord_users.id", ondelete="SET NULL"), nullable=True)
    command_name = Column(String(100), nullable=False)
    command_args = Column(Text, nullable=True)  # JSON string of arguments
    channel_id = Column(String(50), nullable=False)
    guild_id = Column(String(50), nullable=False)
    success = Column(Boolean, default=True)
    execution_time = Column(Numeric(10, 4), nullable=True)  # in seconds
    error_message = Column(Text, nullable=True)
    response_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("DiscordUser", back_populates="commands")


class DiscordBotStatus(Base):
    """Model untuk Discord Bot Status Monitoring"""
    __tablename__ = "discord_bot_status"
    
    id = Column(Integer, primary_key=True, index=True)
    bot_id = Column(Integer, ForeignKey("discord_bots.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), nullable=False)  # online, offline, idle, dnd
    latency = Column(Numeric(10, 4), nullable=True)  # in milliseconds
    guild_count = Column(Integer, default=0)
    user_count = Column(Integer, default=0)
    uptime = Column(Integer, default=0)  # in seconds
    memory_usage = Column(Numeric(10, 2), nullable=True)  # in MB
    cpu_usage = Column(Numeric(5, 2), nullable=True)  # in percentage
    created_at = Column(DateTime(timezone=True), server_default=func.now())
