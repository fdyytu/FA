from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.user import User
from app.models.transaction import UserProfile
from app.schemas.user_profile import (
    UserProfileCreate, UserProfileUpdate, UserProfileResponse,
    UserDetailResponse
)
from app.utils.exceptions import HTTPException
from app.common.base_classes.base_service import BaseService
import logging
import os
import uuid
from fastapi import UploadFile

logger = logging.getLogger(__name__)

class UserProfileService(BaseService):
    """Service untuk mengelola profil user - mengikuti prinsip Single Responsibility"""
    
    def __init__(self, db: Session):
        super().__init__(db)
        self.upload_dir = "static/uploads/avatars"
        os.makedirs(self.upload_dir, exist_ok=True)
    
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
    
    async def upload_avatar(self, user_id: int, file: UploadFile) -> str:
        """Upload avatar user"""
        try:
            # Validasi file
            if not file.content_type.startswith("image/"):
                raise HTTPException(status_code=400, detail="File harus berupa gambar")
            
            # Generate unique filename
            file_extension = file.filename.split(".")[-1]
            unique_filename = f"{user_id}_{uuid.uuid4()}.{file_extension}"
            file_path = os.path.join(self.upload_dir, unique_filename)
            
            # Save file
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            # Update profile dengan avatar URL
            avatar_url = f"/static/uploads/avatars/{unique_filename}"
            profile = self.db.query(UserProfile).filter(
                UserProfile.user_id == user_id
            ).first()
            
            if profile:
                # Hapus avatar lama jika ada
                if profile.avatar_url:
                    old_file_path = profile.avatar_url.replace("/static/", "static/")
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)
                
                profile.avatar_url = avatar_url
                self.db.commit()
            else:
                # Buat profil baru jika belum ada
                new_profile = UserProfile(
                    user_id=user_id,
                    avatar_url=avatar_url
                )
                self.db.add(new_profile)
                self.db.commit()
            
            logger.info(f"Avatar berhasil diupload untuk user_id: {user_id}")
            return avatar_url
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error uploading avatar: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal upload avatar: {str(e)}")
    
    async def delete_avatar(self, user_id: int) -> None:
        """Hapus avatar user"""
        try:
            profile = self.db.query(UserProfile).filter(
                UserProfile.user_id == user_id
            ).first()
            
            if not profile or not profile.avatar_url:
                raise HTTPException(status_code=404, detail="Avatar tidak ditemukan")
            
            # Hapus file dari storage
            file_path = profile.avatar_url.replace("/static/", "static/")
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # Update database
            profile.avatar_url = None
            self.db.commit()
            
            logger.info(f"Avatar berhasil dihapus untuk user_id: {user_id}")
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting avatar: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal hapus avatar: {str(e)}")
    
    async def verify_identity(self, user_id: int) -> UserProfileResponse:
        """Verifikasi identitas user (untuk admin)"""
        try:
            profile = self.db.query(UserProfile).filter(
                UserProfile.user_id == user_id
            ).first()
            
            if not profile:
                raise HTTPException(status_code=404, detail="Profil tidak ditemukan")
            
            profile.identity_verified = "verified"
            self.db.commit()
            self.db.refresh(profile)
            
            logger.info(f"Identitas user berhasil diverifikasi untuk user_id: {user_id}")
            return UserProfileResponse.from_orm(profile)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error verifying user identity: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal verifikasi identitas: {str(e)}")
