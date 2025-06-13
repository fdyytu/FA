from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from fastapi import HTTPException, status
from app.infrastructure.config.settings import settings

class TokenHandler:
    """
    Token handler yang mengimplementasikan Single Responsibility Principle.
    Fokus hanya pada operasi JWT token creation dan validation.
    """
    
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = settings.REFRESH_TOKEN_EXPIRE_DAYS
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Buat access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Buat refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_token_pair(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Buat pasangan access dan refresh token"""
        access_token = self.create_access_token(user_data)
        refresh_token = self.create_refresh_token(user_data)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self.access_token_expire_minutes * 60
        }
    
    def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        """Verifikasi dan decode token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Cek tipe token
            if payload.get("type") != token_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            # Cek expiration
            exp = payload.get("exp")
            if exp is None or datetime.utcnow() > datetime.fromtimestamp(exp):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expired"
                )
            
            return payload
            
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token menggunakan refresh token"""
        payload = self.verify_token(refresh_token, "refresh")
        
        # Buat access token baru dengan data dari refresh token
        user_data = {
            "sub": payload.get("sub"),
            "user_id": payload.get("user_id"),
            "username": payload.get("username")
        }
        
        new_access_token = self.create_access_token(user_data)
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": self.access_token_expire_minutes * 60
        }
    
    def get_token_payload(self, token: str) -> Optional[Dict[str, Any]]:
        """Ambil payload dari token tanpa verifikasi expiration"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm], options={"verify_exp": False})
            return payload
        except JWTError:
            return None
    
    def is_token_expired(self, token: str) -> bool:
        """Cek apakah token sudah expired"""
        payload = self.get_token_payload(token)
        if not payload:
            return True
        
        exp = payload.get("exp")
        if exp is None:
            return True
        
        return datetime.utcnow() > datetime.fromtimestamp(exp)
