from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from app.models.user import User
from app.models.transaction import Transaction, UserProfile
from app.schemas.user_profile import (
    UserDetailResponse, UserListResponse, UserProfileResponse
)
from app.common.exceptions.custom_exceptions import HTTPException
from app.shared.base_classes.base_service import BaseService
from app.common.security.auth_security import get_password_hash
import logging
import secrets
import string
import csv
import io
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class UserManagementService(BaseService):
    """Service untuk mengelola user oleh admin - mengikuti prinsip Single Responsibility"""
    
    def __init__(self, db: Session):
        super().__init__(db)
        self.export_dir = "static/exports"
        os.makedirs(self.export_dir, exist_ok=True)
    
    async def get_users_list(
        self, 
        page: int, 
        limit: int, 
        search: Optional[str] = None,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """Mendapatkan daftar user dengan filter dan pagination"""
        try:
            query = self.db.query(User)
            
            # Filter berdasarkan status
            if status and status != "all":
                if status == "active":
                    query = query.filter(User.is_active == True)
                elif status == "inactive":
                    query = query.filter(User.is_active == False)
            
            # Filter berdasarkan search
            if search:
                search_filter = or_(
                    User.username.ilike(f"%{search}%"),
                    User.email.ilike(f"%{search}%"),
                    User.full_name.ilike(f"%{search}%"),
                    User.phone_number.ilike(f"%{search}%")
                )
                query = query.filter(search_filter)
            
            # Hitung total
            total = query.count()
            total_pages = (total + limit - 1) // limit
            
            # Pagination
            offset = (page - 1) * limit
            users = query.order_by(desc(User.created_at)).offset(offset).limit(limit).all()
            
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
            
            return {
                "users": user_list,
                "total": total,
                "total_pages": total_pages
            }
            
        except Exception as e:
            logger.error(f"Error getting users list: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal mengambil daftar user: {str(e)}")
    
    async def get_user_detail(self, user_id: int) -> UserDetailResponse:
        """Mendapatkan detail user tertentu"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User tidak ditemukan")
            
            # Ambil profil jika ada
            profile = self.db.query(UserProfile).filter(
                UserProfile.user_id == user_id
            ).first()
            
            profile_response = None
            if profile:
                profile_response = UserProfileResponse.from_orm(profile)
            
            user_detail = UserDetailResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                full_name=user.full_name,
                phone_number=user.phone_number,
                balance=float(user.balance),
                is_active=user.is_active,
                created_at=user.created_at,
                profile=profile_response
            )
            
            return user_detail
            
        except Exception as e:
            logger.error(f"Error getting user detail: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal mengambil detail user: {str(e)}")
    
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
            user_detail = await self.get_user_detail(user_id)
            
            logger.info(f"Status user berhasil diubah untuk user_id: {user_id}, status: {user.is_active}")
            return user_detail
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error toggling user status: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal mengubah status user: {str(e)}")
    
    async def verify_user_identity(self, user_id: int) -> UserProfileResponse:
        """Verifikasi identitas user"""
        try:
            profile = self.db.query(UserProfile).filter(
                UserProfile.user_id == user_id
            ).first()
            
            if not profile:
                raise HTTPException(status_code=404, detail="Profil user tidak ditemukan")
            
            profile.identity_verified = "verified"
            self.db.commit()
            self.db.refresh(profile)
            
            logger.info(f"Identitas user berhasil diverifikasi untuk user_id: {user_id}")
            return UserProfileResponse.from_orm(profile)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error verifying user identity: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal verifikasi identitas: {str(e)}")
    
    async def reset_user_password(self, user_id: int) -> str:
        """Reset password user dan generate password sementara"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User tidak ditemukan")
            
            # Generate password sementara
            temp_password = self._generate_temporary_password()
            
            # Hash password dan update
            user.hashed_password = get_password_hash(temp_password)
            self.db.commit()
            
            logger.info(f"Password user berhasil direset untuk user_id: {user_id}")
            return temp_password
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error resetting user password: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal reset password user: {str(e)}")
    
    async def delete_user(self, user_id: int) -> None:
        """Soft delete user"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User tidak ditemukan")
            
            # Soft delete dengan mengubah status dan menambah suffix pada email/username
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            user.is_active = False
            user.email = f"{user.email}_deleted_{timestamp}"
            user.username = f"{user.username}_deleted_{timestamp}"
            
            self.db.commit()
            
            logger.info(f"User berhasil dihapus (soft delete) untuk user_id: {user_id}")
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting user: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal menghapus user: {str(e)}")
    
    async def get_user_statistics(self) -> Dict[str, Any]:
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
            
            # Statistik registrasi user per bulan (6 bulan terakhir)
            monthly_registrations = self.db.query(
                func.date_trunc('month', User.created_at).label('month'),
                func.count(User.id).label('count')
            ).group_by('month').order_by(desc('month')).limit(6).all()
            
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
                ],
                "monthly_registrations": [
                    {
                        "month": reg.month.strftime("%Y-%m"),
                        "count": reg.count
                    } for reg in monthly_registrations
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting user statistics: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal mengambil statistik user: {str(e)}")
    
    async def export_users_data(self, format: str = "csv") -> str:
        """Export data user ke CSV atau Excel"""
        try:
            users = self.db.query(User).all()
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"users_export_{timestamp}.{format}"
            file_path = os.path.join(self.export_dir, filename)
            
            if format == "csv":
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['id', 'username', 'email', 'full_name', 'phone_number', 
                                'balance', 'is_active', 'created_at']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    
                    writer.writeheader()
                    for user in users:
                        writer.writerow({
                            'id': user.id,
                            'username': user.username,
                            'email': user.email,
                            'full_name': user.full_name,
                            'phone_number': user.phone_number,
                            'balance': float(user.balance),
                            'is_active': user.is_active,
                            'created_at': user.created_at.isoformat()
                        })
            
            file_url = f"/static/exports/{filename}"
            logger.info(f"Data user berhasil diexport ke {format.upper()}: {file_url}")
            return file_url
            
        except Exception as e:
            logger.error(f"Error exporting users data: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal export data user: {str(e)}")
    
    def _generate_temporary_password(self, length: int = 12) -> str:
        """Generate password sementara yang aman"""
        characters = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(characters) for _ in range(length))
