from typing import Optional, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.shared.base_classes.base_service import BaseService
from app.domains.auth.repositories.user_repository import UserRepository
from app.domains.auth.models.user import User
from app.domains.auth.schemas.auth_schemas import UserCreate, UserUpdate, PasswordChange
from app.infrastructure.security.password_handler import PasswordHandler
from app.infrastructure.security.token_handler import TokenHandler

class AuthService(BaseService[User, UserRepository]):
    """
    Authentication service yang mengimplementasikan Single Responsibility Principle.
    Fokus hanya pada business logic authentication dan user management.
    """
    
    def __init__(self, repository: UserRepository):
        super().__init__(repository)
        self.password_handler = PasswordHandler()
        self.token_handler = TokenHandler()
    
    def create(self, data: dict) -> User:
        """Buat user baru dengan validasi business rules"""
        # Validasi business rules
        if not self._validate_business_rules(data):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data tidak valid"
            )
        
        # Hook before create
        data = self._before_create(data)
        
        # Hash password
        if 'password' in data:
            data['hashed_password'] = self.password_handler.hash_password(data.pop('password'))
        
        # Cek duplikasi username dan email
        if self.repository.get_by_username(data['username']):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username sudah digunakan"
            )
        
        if self.repository.get_by_email(data['email']):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email sudah digunakan"
            )
        
        # Create user
        user = self.repository.create(data)
        
        # Hook after create
        return self._after_create(user)
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Ambil user berdasarkan ID"""
        user = self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User tidak ditemukan"
            )
        return user
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Ambil semua users dengan pagination"""
        return self.repository.get_all(skip, limit)
    
    def update(self, user_id: int, data: dict) -> Optional[User]:
        """Update user dengan validasi business rules"""
        user = self.get_by_id(user_id)
        
        # Hook before update
        data = self._before_update(user_id, data)
        
        # Validasi email duplikasi jika email diubah
        if 'email' in data and data['email'] != user.email:
            if self.repository.get_by_email(data['email']):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email sudah digunakan"
                )
        
        # Update user
        updated_user = self.repository.update(user_id, data)
        
        # Hook after update
        return self._after_update(updated_user)
    
    def delete(self, user_id: int) -> bool:
        """Soft delete user"""
        user = self.get_by_id(user_id)
        return self.repository.delete(user_id)
    
    # Authentication specific methods
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Autentikasi user dengan username dan password"""
        user = self.repository.get_by_username(username)
        if not user:
            return None
        
        if not self.password_handler.verify_password(password, user.hashed_password):
            return None
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User tidak aktif"
            )
        
        return user
    
    def change_password(self, user_id: int, password_data: PasswordChange) -> bool:
        """Ubah password user"""
        user = self.get_by_id(user_id)
        
        # Verifikasi password lama
        if not self.password_handler.verify_password(password_data.current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password lama tidak benar"
            )
        
        # Hash password baru
        new_hashed_password = self.password_handler.hash_password(password_data.new_password)
        
        # Update password
        return bool(self.repository.update(user_id, {'hashed_password': new_hashed_password}))
    
    def activate_user(self, user_id: int) -> bool:
        """Aktifkan user"""
        return bool(self.repository.update(user_id, {'is_active': True}))
    
    def deactivate_user(self, user_id: int) -> bool:
        """Nonaktifkan user"""
        return bool(self.repository.update(user_id, {'is_active': False}))
    
    def search_users(self, search_term: str, skip: int = 0, limit: int = 100) -> List[User]:
        """Cari users berdasarkan term"""
        return self.repository.search_users(search_term, skip, limit)
    
    def get_user_stats(self) -> dict:
        """Ambil statistik users"""
        total_users = self.repository.count_total_users()
        active_users = self.repository.count_active_users()
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'inactive_users': total_users - active_users
        }
    
    def _validate_business_rules(self, data: dict) -> bool:
        """Validasi business rules untuk user"""
        # Implementasi validasi business rules
        return True
    
    def _before_create(self, data: dict) -> dict:
        """Hook sebelum create user"""
        # Set default values
        data.setdefault('is_active', True)
        data.setdefault('is_superuser', False)
        data.setdefault('balance', 0)
        return data
    
    def _after_create(self, user: User) -> User:
        """Hook setelah create user"""
        # Log user creation, send welcome email, etc.
        return user
    
    def _before_update(self, user_id: int, data: dict) -> dict:
        """Hook sebelum update user"""
        # Remove fields that shouldn't be updated directly
        data.pop('hashed_password', None)
        data.pop('is_superuser', None)
        return data
    
    def _after_update(self, user: User) -> User:
        """Hook setelah update user"""
        # Log user update, send notification, etc.
        return user
