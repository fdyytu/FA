from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from app.models.user import User
from app.models.transaction import UserProfile, Transaction
from app.schemas.user_profile import (
    UserProfileCreate, UserProfileUpdate, UserProfileResponse,
    UserDetailResponse, UserListResponse
)
from app.utils.exceptions import HTTPException
import logging

logger = logging.getLogger(__name__)

class UserProfileService:
    """Service untuk mengelola profil user - mengikuti prinsip Single Responsibility"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_profile(self, user_id: int, profile_data: UserProfileCreate) -> UserProfileResponse:
        """Membuat profil user baru"""
        try:
            # Cek apakah user sudah memiliki profil
            existing_profile = self.db.query(UserProfile).filter(
                UserProfile.user_id == user_id
            ).first()
            
            if existing_profile:
                raise HTTPException(status_code=400, detail="User sudah memiliki profil")
            
            # Cek apakah user ada
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User tidak ditemukan")
            
            # Buat profil baru
            db_profile = UserProfile(
                user_id=user_id,
                **profile_data.dict()
            )
            
            self.db.add(db_profile)
            self.db.commit()
            self.db.refresh(db_profile)
            
            logger.info(f"Profil user berhasil dibuat untuk user_id: {user_id}")
            return UserProfileResponse.from_orm(db_profile)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating user profile: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal membuat profil: {str(e)}")
    
    async def get_profile(self, user_id: int) -> Optional[UserProfileResponse]:
        """Mendapatkan profil user"""
        try:
            profile = self.db.query(UserProfile).filter(
                UserProfile.user_id == user_id
            ).first()
            
            if not profile:
                return None
            
            return UserProfileResponse.from_orm(profile)
            
        except Exception as e:
            logger.error(f"Error getting user profile: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal mengambil profil: {str(e)}")
    
    async def update_profile(self, user_id: int, profile_data: UserProfileUpdate) -> UserProfileResponse:
        """Update profil user"""
        try:
            profile = self.db.query(UserProfile).filter(
                UserProfile.user_id == user_id
            ).first()
            
            if not profile:
                raise HTTPException(status_code=404, detail="Profil tidak ditemukan")
            
            # Update data yang tidak None
            update_data = profile_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(profile, field, value)
            
            self.db.commit()
            self.db.refresh(profile)
            
            logger.info(f"Profil user berhasil diupdate untuk user_id: {user_id}")
            return UserProfileResponse.from_orm(profile)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating user profile: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal update profil: {str(e)}")
    
    async def get_user_detail(self, user_id: int) -> UserDetailResponse:
        """Mendapatkan detail user lengkap dengan profil"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User tidak ditemukan")
            
            # Ambil profil jika ada
            profile = await self.get_profile(user_id)
            
            user_detail = UserDetailResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                full_name=user.full_name,
                phone_number=user.phone_number,
                balance=float(user.balance),
                is_active=user.is_active,
                created_at=user.created_at,
                profile=profile
            )
            
            return user_detail
            
        except Exception as e:
            logger.error(f"Error getting user detail: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal mengambil detail user: {str(e)}")
    
    async def verify_identity(self, user_id: int) -> UserProfileResponse:
        """Verifikasi identitas user (untuk admin)"""
        try:
            profile = self.db.query(UserProfile).filter(
                UserProfile.user_id == user_id
            ).first()
            
            if not profile:
                raise HTTPException(status_code=404, detail="Profil tidak ditemukan")
            
            profile.identity_verified = "1"
            self.db.commit()
            self.db.refresh(profile)
            
            logger.info(f"Identitas user berhasil diverifikasi untuk user_id: {user_id}")
            return UserProfileResponse.from_orm(profile)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error verifying user identity: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal verifikasi identitas: {str(e)}")

class UserManagementService:
    """Service untuk manajemen user oleh admin - mengikuti prinsip Single Responsibility"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_users_list(self, page: int = 1, limit: int = 10, search: Optional[str] = None) -> List[UserListResponse]:
        """Mendapatkan daftar user untuk admin"""
        try:
            query = self.db.query(User)
            
            # Filter pencarian
            if search:
                query = query.filter(
                    or_(
                        User.username.ilike(f"%{search}%"),
                        User.email.ilike(f"%{search}%"),
                        User.full_name.ilike(f"%{search}%")
                    )
                )
            
            # Pagination
            offset = (page - 1) * limit
            users = query.offset(offset).limit(limit).all()
            
            # Ambil statistik transaksi untuk setiap user
            user_list = []
            for user in users:
                # Hitung total transaksi dan tanggal transaksi terakhir
                transaction_stats = self.db.query(
                    func.count(Transaction.id).label('total_transactions'),
                    func.max(Transaction.created_at).label('last_transaction_date')
                ).filter(Transaction.user_id == user.id).first()
                
                user_data = UserListResponse(
                    id=user.id,
                    username=user.username,
                    email=user.email,
                    full_name=user.full_name,
                    phone_number=user.phone_number,
                    balance=float(user.balance),
                    is_active=user.is_active,
                    created_at=user.created_at,
                    total_transactions=transaction_stats.total_transactions or 0,
                    last_transaction_date=transaction_stats.last_transaction_date
                )
                user_list.append(user_data)
            
            return user_list
            
        except Exception as e:
            logger.error(f"Error getting users list: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal mengambil daftar user: {str(e)}")
    
    async def toggle_user_status(self, user_id: int) -> UserDetailResponse:
        """Toggle status aktif/nonaktif user"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User tidak ditemukan")
            
            user.is_active = not user.is_active
            self.db.commit()
            self.db.refresh(user)
            
            # Ambil detail user lengkap
            profile_service = UserProfileService(self.db)
            user_detail = await profile_service.get_user_detail(user_id)
            
            logger.info(f"Status user berhasil diubah untuk user_id: {user_id}, status: {user.is_active}")
            return user_detail
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error toggling user status: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal mengubah status user: {str(e)}")
    
    async def get_user_statistics(self) -> dict:
        """Mendapatkan statistik user untuk dashboard admin"""
        try:
            total_users = self.db.query(func.count(User.id)).scalar()
            active_users = self.db.query(func.count(User.id)).filter(User.is_active == True).scalar()
            inactive_users = total_users - active_users
            
            # User dengan saldo terbanyak
            top_balance_users = self.db.query(User).order_by(desc(User.balance)).limit(5).all()
            
            # User dengan transaksi terbanyak
            top_transaction_users = self.db.query(
                User.id, User.username, User.full_name,
                func.count(Transaction.id).label('transaction_count')
            ).join(Transaction).group_by(User.id).order_by(desc('transaction_count')).limit(5).all()
            
            return {
                "total_users": total_users,
                "active_users": active_users,
                "inactive_users": inactive_users,
                "top_balance_users": [
                    {
                        "id": user.id,
                        "username": user.username,
                        "full_name": user.full_name,
                        "balance": float(user.balance)
                    } for user in top_balance_users
                ],
                "top_transaction_users": [
                    {
                        "id": user.id,
                        "username": user.username,
                        "full_name": user.full_name,
                        "transaction_count": user.transaction_count
                    } for user in top_transaction_users
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting user statistics: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal mengambil statistik user: {str(e)}")
