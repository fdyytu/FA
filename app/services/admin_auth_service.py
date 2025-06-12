from typing import Optional
from fastapi import HTTPException, status
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.core.config import settings
from app.schemas.product import AdminLoginRequest, AdminLoginResponse
import logging

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AdminAuthService:
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifikasi password"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash password"""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Buat access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> dict:
        """Verifikasi token"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token tidak valid"
                )
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token tidak valid"
            )
    
    @staticmethod
    def authenticate_admin(login_data: AdminLoginRequest) -> AdminLoginResponse:
        """Autentikasi admin"""
        # Cek kredensial admin dari settings
        if (login_data.username != settings.ADMIN_USERNAME or 
            login_data.password != settings.ADMIN_PASSWORD):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Username atau password salah"
            )
        
        # Buat access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = AdminAuthService.create_access_token(
            data={"sub": login_data.username, "type": "admin"},
            expires_delta=access_token_expires
        )
        
        logger.info(f"Admin {login_data.username} berhasil login")
        
        return AdminLoginResponse(
            access_token=access_token,
            token_type="bearer",
            message="Login berhasil"
        )
    
    @staticmethod
    def get_current_admin(token: str) -> dict:
        """Ambil data admin dari token"""
        payload = AdminAuthService.verify_token(token)
        
        # Pastikan token adalah untuk admin
        if payload.get("type") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Akses ditolak. Token bukan untuk admin."
            )
        
        return {
            "username": payload.get("sub"),
            "type": payload.get("type")
        }
