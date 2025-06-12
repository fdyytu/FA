from passlib.context import CryptContext
from typing import Union

class PasswordHandler:
    """
    Password handler yang mengimplementasikan Single Responsibility Principle.
    Fokus hanya pada operasi password hashing dan verification.
    """
    
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def hash_password(self, password: str) -> str:
        """Hash password menggunakan bcrypt"""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verifikasi password dengan hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def is_password_strong(self, password: str) -> bool:
        """Cek apakah password memenuhi kriteria strong password"""
        if len(password) < 8:
            return False
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        return has_upper and has_lower and has_digit and has_special
