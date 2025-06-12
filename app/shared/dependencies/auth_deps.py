from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.infrastructure.database.database_manager import get_db
from app.infrastructure.security.token_handler import TokenHandler
from app.domains.auth.repositories.user_repository import UserRepository
from app.domains.auth.models.user import User

# Security
security = HTTPBearer()
token_handler = TokenHandler()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency untuk mendapatkan current user dari token.
    Mengimplementasikan Dependency Inversion Principle.
    """
    try:
        # Verifikasi token
        payload = token_handler.verify_token(credentials.credentials)
        user_id = payload.get("user_id")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Ambil user dari database
        user_repository = UserRepository(db)
        user = user_repository.get_by_id(user_id)
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User is inactive"
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Dependency untuk mendapatkan current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

def get_current_superuser(current_user: User = Depends(get_current_user)) -> User:
    """Dependency untuk mendapatkan current superuser"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

# Repository dependencies
def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    """Dependency untuk mendapatkan UserRepository"""
    return UserRepository(db)
