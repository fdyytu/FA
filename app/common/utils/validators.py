from typing import Any
import re
from fastapi import HTTPException, status

def validate_email(email: str) -> bool:
    """Validasi format email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone_number(phone: str) -> bool:
    """Validasi nomor telepon Indonesia"""
    # Format: 08xxxxxxxxxx atau +628xxxxxxxxxx
    pattern = r'^(\+628|08)[0-9]{8,12}$'
    return re.match(pattern, phone) is not None

def validate_customer_number(category: str, customer_number: str) -> bool:
    """Validasi nomor pelanggan berdasarkan kategori"""
    if category == "pulsa":
        # Nomor HP: 08xxxxxxxxxx
        return validate_phone_number(customer_number)
    elif category == "listrik":
        # Nomor meter PLN: 11-12 digit
        return len(customer_number) >= 11 and customer_number.isdigit()
    elif category == "pdam":
        # Nomor pelanggan PDAM: 6-15 karakter
        return 6 <= len(customer_number) <= 15
    else:
        # Default: minimal 3 karakter
        return len(customer_number) >= 3

def validate_password_strength(password: str) -> tuple[bool, str]:
    """Validasi kekuatan password"""
    if len(password) < 8:
        return False, "Password minimal 8 karakter"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password harus mengandung huruf besar"
    
    if not re.search(r'[a-z]', password):
        return False, "Password harus mengandung huruf kecil"
    
    if not re.search(r'[0-9]', password):
        return False, "Password harus mengandung angka"
    
    return True, "Password valid"

def sanitize_input(value: Any) -> str:
    """Sanitasi input untuk mencegah injection"""
    if value is None:
        return ""
    
    # Convert ke string dan hapus karakter berbahaya
    sanitized = str(value).strip()
    dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '|', '`']
    
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    
    return sanitized
