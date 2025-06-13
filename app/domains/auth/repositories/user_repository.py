from typing import Optional, List
from sqlalchemy.orm import Session
from app.domains.auth.models.user import User

class UserRepository:
    """
    User repository yang mengimplementasikan Dependency Inversion Principle.
    Memisahkan logic data access dari business logic.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.model = User
    
    def create(self, obj_data: dict) -> User:
        """Buat user baru"""
        user = User(**obj_data)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Ambil user berdasarkan ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Ambil semua users dengan pagination"""
        return self.db.query(User).offset(skip).limit(limit).all()
    
    def update(self, user_id: int, obj_data: dict) -> Optional[User]:
        """Update user"""
        user = self.get_by_id(user_id)
        if user:
            for key, value in obj_data.items():
                setattr(user, key, value)
            self.db.commit()
            self.db.refresh(user)
            return user
        return None
    
    def delete(self, user_id: int) -> bool:
        """Hapus user (soft delete dengan mengubah is_active)"""
        user = self.get_by_id(user_id)
        if user:
            user.is_active = False
            self.db.commit()
            return True
        return False
    
    # Domain-specific methods
    def get_by_username(self, username: str) -> Optional[User]:
        """Ambil user berdasarkan username"""
        return self.db.query(User).filter(User.username == username).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Ambil user berdasarkan email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Ambil semua active users"""
        return self.db.query(User).filter(User.is_active == True).offset(skip).limit(limit).all()
    
    def search_users(self, search_term: str, skip: int = 0, limit: int = 100) -> List[User]:
        """Cari users berdasarkan username, email, atau full_name"""
        return self.db.query(User).filter(
            (User.username.ilike(f"%{search_term}%")) |
            (User.email.ilike(f"%{search_term}%")) |
            (User.full_name.ilike(f"%{search_term}%"))
        ).offset(skip).limit(limit).all()
    
    def count_total_users(self) -> int:
        """Hitung total users"""
        return self.db.query(User).count()
    
    def count_active_users(self) -> int:
        """Hitung total active users"""
        return self.db.query(User).filter(User.is_active == True).count()
