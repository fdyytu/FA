from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.core.database import get_db

# Try to import Discord models
try:
    from app.models.discord import (
        DiscordBot, DiscordChannel, DiscordUser, DiscordWallet,
        LiveStock, AdminWorldConfig, DiscordBotConfig, DiscordBotStatus
    )
except ImportError:
    DiscordBot = DiscordChannel = DiscordUser = DiscordWallet = None
    LiveStock = AdminWorldConfig = DiscordBotConfig = DiscordBotStatus = None

# Try to import Discord schemas
try:
    from app.schemas.discord import (
        DiscordBotCreate, DiscordBotUpdate, DiscordBotResponse,
        DiscordChannelCreate, DiscordChannelUpdate, DiscordChannelResponse,
        LiveStockCreate, LiveStockUpdate, LiveStockResponse,
        AdminWorldConfigCreate, AdminWorldConfigUpdate, AdminWorldConfigResponse,
        DiscordBotConfigCreate, DiscordBotConfigUpdate, DiscordBotConfigResponse
    )
except ImportError:
    DiscordBotCreate = DiscordBotUpdate = DiscordBotResponse = None
    DiscordChannelCreate = DiscordChannelUpdate = DiscordChannelResponse = None
    LiveStockCreate = LiveStockUpdate = LiveStockResponse = None
    AdminWorldConfigCreate = AdminWorldConfigUpdate = AdminWorldConfigResponse = None
    DiscordBotConfigCreate = DiscordBotConfigUpdate = DiscordBotConfigResponse = None

# Try to import Discord service
try:
    from app.services.discord_bot_service import DiscordBotService
except ImportError:
    DiscordBotService = None

# Try to import utility functions
try:
    from app.utils.responses import create_success_response, create_error_response
except ImportError:
    def create_success_response(data, message="Success"):
        return {"success": True, "data": data, "message": message}
    def create_error_response(message, status_code=400):
        return {"success": False, "message": message, "status_code": status_code}

router = APIRouter()
logger = logging.getLogger(__name__)

# Global bot service instance
bot_service = DiscordBotService() if DiscordBotService else None

# Discord Bot Management
@router.post("/bots", response_model=dict)
async def create_discord_bot(
    bot_data: DiscordBotCreate,
    db: Session = Depends(get_db)
):
    """Buat konfigurasi Discord Bot baru"""
    try:
        # Check if bot already exists for this guild
        existing_bot = db.query(DiscordBot).filter(
            DiscordBot.guild_id == bot_data.guild_id
        ).first()
        
        if existing_bot:
            raise HTTPException(
                status_code=400,
                detail="Bot sudah ada untuk guild ini"
            )
        
        # Create new bot
        new_bot = DiscordBot(**bot_data.dict())
        db.add(new_bot)
        db.commit()
        db.refresh(new_bot)
        
        return create_success_response(
            data=DiscordBotResponse.from_orm(new_bot),
            message="Discord Bot berhasil dibuat"
        )
        
    except Exception as e:
        logger.error(f"Error creating Discord bot: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/bots", response_model=dict)
async def get_discord_bots(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Ambil daftar Discord Bot"""
    try:
        bots = db.query(DiscordBot).offset(skip).limit(limit).all()
        total = db.query(DiscordBot).count()
        
        return create_success_response(
            data={
                "bots": [DiscordBotResponse.from_orm(bot) for bot in bots],
                "total": total,
                "skip": skip,
                "limit": limit
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting Discord bots: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/bots/{bot_id}", response_model=dict)
async def get_discord_bot(
    bot_id: int,
    db: Session = Depends(get_db)
):
    """Ambil detail Discord Bot"""
    try:
        bot = db.query(DiscordBot).filter(DiscordBot.id == bot_id).first()
        if not bot:
            raise HTTPException(status_code=404, detail="Bot tidak ditemukan")
        
        return create_success_response(
            data=DiscordBotResponse.from_orm(bot)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Discord bot: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/bots/{bot_id}", response_model=dict)
async def update_discord_bot(
    bot_id: int,
    bot_data: DiscordBotUpdate,
    db: Session = Depends(get_db)
):
    """Update konfigurasi Discord Bot"""
    try:
        bot = db.query(DiscordBot).filter(DiscordBot.id == bot_id).first()
        if not bot:
            raise HTTPException(status_code=404, detail="Bot tidak ditemukan")
        
        # Update fields
        for field, value in bot_data.dict(exclude_unset=True).items():
            setattr(bot, field, value)
        
        db.commit()
        db.refresh(bot)
        
        return create_success_response(
            data=DiscordBotResponse.from_orm(bot),
            message="Discord Bot berhasil diupdate"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating Discord bot: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bots/{bot_id}/start", response_model=dict)
async def start_discord_bot(
    bot_id: int,
    db: Session = Depends(get_db)
):
    """Start Discord Bot"""
    try:
        bot = db.query(DiscordBot).filter(DiscordBot.id == bot_id).first()
        if not bot:
            raise HTTPException(status_code=404, detail="Bot tidak ditemukan")
        
        # Initialize and start bot
        await bot_service.initialize_bot(bot_id, db)
        
        # Update status
        bot.status = "active"
        db.commit()
        
        # Start bot in background
        import asyncio
        asyncio.create_task(bot_service.start_bot())
        
        return create_success_response(
            message="Discord Bot berhasil distart"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting Discord bot: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bots/{bot_id}/stop", response_model=dict)
async def stop_discord_bot(
    bot_id: int,
    db: Session = Depends(get_db)
):
    """Stop Discord Bot"""
    try:
        bot = db.query(DiscordBot).filter(DiscordBot.id == bot_id).first()
        if not bot:
            raise HTTPException(status_code=404, detail="Bot tidak ditemukan")
        
        # Stop bot
        await bot_service.stop_bot()
        
        # Update status
        bot.status = DiscordBotStatus.INACTIVE
        db.commit()
        
        return create_success_response(
            message="Discord Bot berhasil dihentikan"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping Discord bot: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Live Stock Management
@router.post("/live-stocks", response_model=dict)
async def create_live_stock(
    stock_data: LiveStockCreate,
    db: Session = Depends(get_db)
):
    """Tambah produk ke live stock"""
    try:
        # Check if product code already exists for this bot
        existing_stock = db.query(LiveStock).filter(
            LiveStock.bot_id == stock_data.bot_id,
            LiveStock.product_code == stock_data.product_code
        ).first()
        
        if existing_stock:
            raise HTTPException(
                status_code=400,
                detail="Produk dengan kode ini sudah ada"
            )
        
        new_stock = LiveStock(**stock_data.dict())
        db.add(new_stock)
        db.commit()
        db.refresh(new_stock)
        
        return create_success_response(
            data=LiveStockResponse.from_orm(new_stock),
            message="Produk berhasil ditambahkan ke live stock"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating live stock: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/live-stocks", response_model=dict)
async def get_live_stocks(
    bot_id: Optional[int] = None,
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Ambil daftar live stock"""
    try:
        query = db.query(LiveStock)
        
        if bot_id:
            query = query.filter(LiveStock.bot_id == bot_id)
        if category:
            query = query.filter(LiveStock.category == category)
        if is_active is not None:
            query = query.filter(LiveStock.is_active == is_active)
        
        stocks = query.order_by(LiveStock.display_order, LiveStock.product_name).offset(skip).limit(limit).all()
        total = query.count()
        
        return create_success_response(
            data={
                "stocks": [LiveStockResponse.from_orm(stock) for stock in stocks],
                "total": total,
                "skip": skip,
                "limit": limit
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting live stocks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/live-stocks/{stock_id}", response_model=dict)
async def update_live_stock(
    stock_id: int,
    stock_data: LiveStockUpdate,
    db: Session = Depends(get_db)
):
    """Update produk live stock"""
    try:
        stock = db.query(LiveStock).filter(LiveStock.id == stock_id).first()
        if not stock:
            raise HTTPException(status_code=404, detail="Produk tidak ditemukan")
        
        # Update fields
        for field, value in stock_data.dict(exclude_unset=True).items():
            setattr(stock, field, value)
        
        db.commit()
        db.refresh(stock)
        
        return create_success_response(
            data=LiveStockResponse.from_orm(stock),
            message="Produk berhasil diupdate"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating live stock: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/live-stocks/{stock_id}", response_model=dict)
async def delete_live_stock(
    stock_id: int,
    db: Session = Depends(get_db)
):
    """Hapus produk dari live stock"""
    try:
        stock = db.query(LiveStock).filter(LiveStock.id == stock_id).first()
        if not stock:
            raise HTTPException(status_code=404, detail="Produk tidak ditemukan")
        
        db.delete(stock)
        db.commit()
        
        return create_success_response(
            message="Produk berhasil dihapus dari live stock"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting live stock: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Admin World Configuration
@router.post("/world-configs", response_model=dict)
async def create_world_config(
    world_data: AdminWorldConfigCreate,
    db: Session = Depends(get_db)
):
    """Tambah konfigurasi world admin"""
    try:
        new_world = AdminWorldConfig(**world_data.dict())
        db.add(new_world)
        db.commit()
        db.refresh(new_world)
        
        return create_success_response(
            data=AdminWorldConfigResponse.from_orm(new_world),
            message="World config berhasil ditambahkan"
        )
        
    except Exception as e:
        logger.error(f"Error creating world config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/world-configs", response_model=dict)
async def get_world_configs(
    is_active: Optional[bool] = None,
    access_level: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Ambil daftar world config"""
    try:
        query = db.query(AdminWorldConfig)
        
        if is_active is not None:
            query = query.filter(AdminWorldConfig.is_active == is_active)
        if access_level:
            query = query.filter(AdminWorldConfig.access_level == access_level)
        
        worlds = query.offset(skip).limit(limit).all()
        total = query.count()
        
        return create_success_response(
            data={
                "worlds": [AdminWorldConfigResponse.from_orm(world) for world in worlds],
                "total": total,
                "skip": skip,
                "limit": limit
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting world configs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/world-configs/{world_id}", response_model=dict)
async def update_world_config(
    world_id: int,
    world_data: AdminWorldConfigUpdate,
    db: Session = Depends(get_db)
):
    """Update world config"""
    try:
        world = db.query(AdminWorldConfig).filter(AdminWorldConfig.id == world_id).first()
        if not world:
            raise HTTPException(status_code=404, detail="World config tidak ditemukan")
        
        # Update fields
        for field, value in world_data.dict(exclude_unset=True).items():
            setattr(world, field, value)
        
        db.commit()
        db.refresh(world)
        
        return create_success_response(
            data=AdminWorldConfigResponse.from_orm(world),
            message="World config berhasil diupdate"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating world config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Discord Bot Configuration
@router.post("/bot-configs", response_model=dict)
async def create_bot_config(
    config_data: DiscordBotConfigCreate,
    db: Session = Depends(get_db)
):
    """Tambah konfigurasi bot"""
    try:
        # Check if config key already exists
        existing_config = db.query(DiscordBotConfig).filter(
            DiscordBotConfig.config_key == config_data.config_key
        ).first()
        
        if existing_config:
            raise HTTPException(
                status_code=400,
                detail="Config key sudah ada"
            )
        
        new_config = DiscordBotConfig(**config_data.dict())
        db.add(new_config)
        db.commit()
        db.refresh(new_config)
        
        return create_success_response(
            data=DiscordBotConfigResponse.from_orm(new_config),
            message="Bot config berhasil ditambahkan"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating bot config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/bot-configs", response_model=dict)
async def get_bot_configs(
    config_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Ambil daftar bot config"""
    try:
        query = db.query(DiscordBotConfig)
        
        if config_type:
            query = query.filter(DiscordBotConfig.config_type == config_type)
        if is_active is not None:
            query = query.filter(DiscordBotConfig.is_active == is_active)
        
        configs = query.offset(skip).limit(limit).all()
        total = query.count()
        
        return create_success_response(
            data={
                "configs": [DiscordBotConfigResponse.from_orm(config) for config in configs],
                "total": total,
                "skip": skip,
                "limit": limit
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting bot configs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/bot-configs/{config_id}", response_model=dict)
async def update_bot_config(
    config_id: int,
    config_data: DiscordBotConfigUpdate,
    db: Session = Depends(get_db)
):
    """Update bot config"""
    try:
        config = db.query(DiscordBotConfig).filter(DiscordBotConfig.id == config_id).first()
        if not config:
            raise HTTPException(status_code=404, detail="Bot config tidak ditemukan")
        
        # Update fields
        for field, value in config_data.dict(exclude_unset=True).items():
            setattr(config, field, value)
        
        db.commit()
        db.refresh(config)
        
        return create_success_response(
            data=DiscordBotConfigResponse.from_orm(config),
            message="Bot config berhasil diupdate"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating bot config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Discord Users Management
@router.get("/discord-users", response_model=dict)
async def get_discord_users(
    is_verified: Optional[bool] = None,
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Ambil daftar Discord users"""
    try:
        query = db.query(DiscordUser)
        
        if is_verified is not None:
            query = query.filter(DiscordUser.is_verified == is_verified)
        if is_active is not None:
            query = query.filter(DiscordUser.is_active == is_active)
        
        users = query.offset(skip).limit(limit).all()
        total = query.count()
        
        return create_success_response(
            data={
                "users": [
                    {
                        "id": user.id,
                        "discord_id": user.discord_id,
                        "discord_username": user.discord_username,
                        "grow_id": user.grow_id,
                        "is_verified": user.is_verified,
                        "is_active": user.is_active,
                        "wallet": {
                            "wl_balance": float(user.discord_wallet.wl_balance) if user.discord_wallet else 0,
                            "dl_balance": float(user.discord_wallet.dl_balance) if user.discord_wallet else 0,
                            "bgl_balance": float(user.discord_wallet.bgl_balance) if user.discord_wallet else 0,
                        } if user.discord_wallet else None,
                        "created_at": user.created_at,
                        "updated_at": user.updated_at
                    }
                    for user in users
                ],
                "total": total,
                "skip": skip,
                "limit": limit
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting Discord users: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Statistics
@router.get("/stats", response_model=dict)
async def get_discord_stats(db: Session = Depends(get_db)):
    """Ambil statistik Discord Bot"""
    try:
        total_bots = db.query(DiscordBot).count()
        active_bots = db.query(DiscordBot).filter(DiscordBot.status == "active").count()
        total_users = db.query(DiscordUser).count()
        verified_users = db.query(DiscordUser).filter(DiscordUser.is_verified == True).count()
        total_products = db.query(LiveStock).count()
        active_products = db.query(LiveStock).filter(LiveStock.is_active == True).count()
        total_worlds = db.query(AdminWorldConfig).count()
        active_worlds = db.query(AdminWorldConfig).filter(AdminWorldConfig.is_active == True).count()
        
        return create_success_response(
            data={
                "bots": {
                    "total": total_bots,
                    "active": active_bots,
                    "inactive": total_bots - active_bots
                },
                "users": {
                    "total": total_users,
                    "verified": verified_users,
                    "unverified": total_users - verified_users
                },
                "products": {
                    "total": total_products,
                    "active": active_products,
                    "inactive": total_products - active_products
                },
                "worlds": {
                    "total": total_worlds,
                    "active": active_worlds,
                    "inactive": total_worlds - active_worlds
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting Discord stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
