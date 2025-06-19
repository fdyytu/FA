from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.core.database import get_db

# Try to import Discord models
try:
    from app.models.discord import DiscordUser, DiscordWallet
except ImportError:
    DiscordUser = DiscordWallet = None

# Try to import utility functions
try:
    from app.utils.responses import create_success_response, create_error_response
except ImportError:
    def create_success_response(data, message="Success"):
        return {"success": True, "data": data, "message": message}
    def create_error_response(message, status_code=400):
        return {"success": False, "message": message, "status_code": status_code}

logger = logging.getLogger(__name__)


class DiscordUserController:
    """
    Controller untuk manajemen Discord User - Single Responsibility: Discord user management endpoints
    """
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes untuk manajemen Discord User"""
        
        @self.router.get("/", response_model=dict)
        async def get_discord_users(
            skip: int = 0,
            limit: int = 100,
            db: Session = Depends(get_db)
        ):
            """Ambil daftar Discord User"""
            try:
                if not DiscordUser:
                    return create_success_response(
                        data={
                            "users": [],
                            "total": 0,
                            "skip": skip,
                            "limit": limit
                        }
                    )

                users = db.query(DiscordUser).offset(skip).limit(limit).all()
                total = db.query(DiscordUser).count()
                
                return create_success_response(
                    data={
                        "users": [
                            {
                                "id": user.id,
                                "discord_id": user.discord_id,
                                "username": user.username,
                                "display_name": user.display_name,
                                "is_verified": user.is_verified,
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
        
        @self.router.get("/{user_id}", response_model=dict)
        async def get_discord_user(
            user_id: str,
            db: Session = Depends(get_db)
        ):
            """Ambil detail Discord User"""
            try:
                if not DiscordUser:
                    return create_error_response("Discord User model not available", 503)

                user = db.query(DiscordUser).filter(DiscordUser.id == user_id).first()
                
                if not user:
                    raise HTTPException(status_code=404, detail="Discord User tidak ditemukan")
                
                user_data = {
                    "id": user.id,
                    "discord_id": user.discord_id,
                    "username": user.username,
                    "display_name": user.display_name,
                    "is_verified": user.is_verified,
                    "wallet": {
                        "wl_balance": float(user.discord_wallet.wl_balance) if user.discord_wallet else 0,
                        "dl_balance": float(user.discord_wallet.dl_balance) if user.discord_wallet else 0,
                        "bgl_balance": float(user.discord_wallet.bgl_balance) if user.discord_wallet else 0,
                    } if user.discord_wallet else None,
                    "created_at": user.created_at,
                    "updated_at": user.updated_at
                }
                
                return create_success_response(data=user_data)
                
            except Exception as e:
                logger.error(f"Error getting Discord user {user_id}: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.put("/{user_id}/verify")
        async def verify_discord_user(
            user_id: str,
            db: Session = Depends(get_db)
        ):
            """Verifikasi Discord User"""
            try:
                if not DiscordUser:
                    return create_error_response("Discord User model not available", 503)

                user = db.query(DiscordUser).filter(DiscordUser.id == user_id).first()
                
                if not user:
                    raise HTTPException(status_code=404, detail="Discord User tidak ditemukan")
                
                user.is_verified = True
                db.commit()
                
                return create_success_response(message="Discord User berhasil diverifikasi")
                
            except Exception as e:
                logger.error(f"Error verifying Discord user {user_id}: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.put("/{user_id}/unverify")
        async def unverify_discord_user(
            user_id: str,
            db: Session = Depends(get_db)
        ):
            """Batalkan verifikasi Discord User"""
            try:
                if not DiscordUser:
                    return create_error_response("Discord User model not available", 503)

                user = db.query(DiscordUser).filter(DiscordUser.id == user_id).first()
                
                if not user:
                    raise HTTPException(status_code=404, detail="Discord User tidak ditemukan")
                
                user.is_verified = False
                db.commit()
                
                return create_success_response(message="Verifikasi Discord User berhasil dibatalkan")
                
            except Exception as e:
                logger.error(f"Error unverifying Discord user {user_id}: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/{user_id}/wallet", response_model=dict)
        async def get_user_wallet(
            user_id: str,
            db: Session = Depends(get_db)
        ):
            """Ambil wallet Discord User"""
            try:
                if not DiscordWallet:
                    return create_error_response("Discord Wallet model not available", 503)

                wallet = db.query(DiscordWallet).filter(DiscordWallet.user_id == user_id).first()
                
                if not wallet:
                    # Create wallet if not exists
                    wallet = DiscordWallet(
                        user_id=user_id,
                        wl_balance=0,
                        dl_balance=0,
                        bgl_balance=0
                    )
                    db.add(wallet)
                    db.commit()
                    db.refresh(wallet)
                
                wallet_data = {
                    "user_id": wallet.user_id,
                    "wl_balance": float(wallet.wl_balance),
                    "dl_balance": float(wallet.dl_balance),
                    "bgl_balance": float(wallet.bgl_balance),
                    "created_at": wallet.created_at,
                    "updated_at": wallet.updated_at
                }
                
                return create_success_response(data=wallet_data)
                
            except Exception as e:
                logger.error(f"Error getting Discord user wallet {user_id}: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.put("/{user_id}/wallet/balance")
        async def update_user_wallet_balance(
            user_id: str,
            wl_balance: Optional[float] = None,
            dl_balance: Optional[float] = None,
            bgl_balance: Optional[float] = None,
            db: Session = Depends(get_db)
        ):
            """Update balance wallet Discord User"""
            try:
                if not DiscordWallet:
                    return create_error_response("Discord Wallet model not available", 503)

                wallet = db.query(DiscordWallet).filter(DiscordWallet.user_id == user_id).first()
                
                if not wallet:
                    # Create wallet if not exists
                    wallet = DiscordWallet(
                        user_id=user_id,
                        wl_balance=wl_balance or 0,
                        dl_balance=dl_balance or 0,
                        bgl_balance=bgl_balance or 0
                    )
                    db.add(wallet)
                else:
                    # Update existing wallet
                    if wl_balance is not None:
                        wallet.wl_balance = wl_balance
                    if dl_balance is not None:
                        wallet.dl_balance = dl_balance
                    if bgl_balance is not None:
                        wallet.bgl_balance = bgl_balance
                
                db.commit()
                db.refresh(wallet)
                
                return create_success_response(
                    data={
                        "wl_balance": float(wallet.wl_balance),
                        "dl_balance": float(wallet.dl_balance),
                        "bgl_balance": float(wallet.bgl_balance)
                    },
                    message="Balance wallet berhasil diupdate"
                )
                
            except Exception as e:
                logger.error(f"Error updating Discord user wallet balance {user_id}: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/stats/summary")
        async def get_user_stats(
            db: Session = Depends(get_db)
        ):
            """Ambil statistik Discord User"""
            try:
                if not DiscordUser:
                    return create_success_response(
                        data={
                            "total_users": 0,
                            "verified_users": 0,
                            "unverified_users": 0,
                            "users_with_wallet": 0
                        }
                    )

                total_users = db.query(DiscordUser).count()
                verified_users = db.query(DiscordUser).filter(DiscordUser.is_verified == True).count()
                users_with_wallet = db.query(DiscordWallet).count() if DiscordWallet else 0
                
                stats = {
                    "total_users": total_users,
                    "verified_users": verified_users,
                    "unverified_users": total_users - verified_users,
                    "users_with_wallet": users_with_wallet
                }
                
                return create_success_response(data=stats)
                
            except Exception as e:
                logger.error(f"Error getting Discord user stats: {e}")
                raise HTTPException(status_code=500, detail=str(e))


# Initialize controller
user_controller = DiscordUserController()
