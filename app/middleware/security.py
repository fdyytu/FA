from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user import User
from functools import wraps
import logging

logger = logging.getLogger(__name__)

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Middleware untuk memastikan user adalah admin"""
    if not current_user.is_admin:
        logger.warning(f"Non-admin user {current_user.id} attempted to access admin endpoint")
        raise HTTPException(
            status_code=403, 
            detail="Akses ditolak. Hanya admin yang dapat mengakses endpoint ini."
        )
    return current_user

def require_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Middleware untuk memastikan user aktif"""
    if not current_user.is_active:
        logger.warning(f"Inactive user {current_user.id} attempted to access endpoint")
        raise HTTPException(
            status_code=403, 
            detail="Akun Anda tidak aktif. Silakan hubungi administrator."
        )
    return current_user

def require_verified_user(current_user: User = Depends(get_current_user)) -> User:
    """Middleware untuk memastikan user sudah terverifikasi"""
    # Implementasi verifikasi bisa disesuaikan dengan kebutuhan
    # Misalnya cek email verification, phone verification, dll
    if not current_user.is_active:
        raise HTTPException(
            status_code=403, 
            detail="Akun Anda belum terverifikasi. Silakan verifikasi akun terlebih dahulu."
        )
    return current_user

class RateLimiter:
    """Rate limiter middleware untuk mencegah spam"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 3600):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}  # Dalam implementasi nyata, gunakan Redis
    
    def __call__(self, user_id: int) -> bool:
        """Check if user has exceeded rate limit"""
        import time
        current_time = time.time()
        
        # Clean old entries
        self.requests = {
            uid: timestamps for uid, timestamps in self.requests.items()
            if any(ts > current_time - self.window_seconds for ts in timestamps)
        }
        
        # Get user's recent requests
        user_requests = self.requests.get(user_id, [])
        recent_requests = [ts for ts in user_requests if ts > current_time - self.window_seconds]
        
        if len(recent_requests) >= self.max_requests:
            return False
        
        # Add current request
        recent_requests.append(current_time)
        self.requests[user_id] = recent_requests
        
        return True

# Global rate limiter instances
api_rate_limiter = RateLimiter(max_requests=1000, window_seconds=3600)  # 1000 requests per hour
auth_rate_limiter = RateLimiter(max_requests=10, window_seconds=300)    # 10 auth attempts per 5 minutes

def rate_limit_check(limiter: RateLimiter):
    """Decorator untuk rate limiting"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user_id from current_user dependency
            current_user = None
            for arg in args:
                if isinstance(arg, User):
                    current_user = arg
                    break
            
            if current_user and not limiter(current_user.id):
                raise HTTPException(
                    status_code=429,
                    detail="Terlalu banyak permintaan. Silakan coba lagi nanti."
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def log_user_activity(activity_type: str, description: str = ""):
    """Decorator untuk logging aktivitas user"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user_id from current_user dependency
            current_user = None
            for arg in args:
                if isinstance(arg, User):
                    current_user = arg
                    break
            
            try:
                result = await func(*args, **kwargs)
                
                if current_user:
                    logger.info(f"User Activity - user_id: {current_user.id}, "
                              f"activity: {activity_type}, "
                              f"description: {description}, "
                              f"endpoint: {func.__name__}")
                
                return result
            except Exception as e:
                if current_user:
                    logger.error(f"User Activity Error - user_id: {current_user.id}, "
                               f"activity: {activity_type}, "
                               f"error: {str(e)}, "
                               f"endpoint: {func.__name__}")
                raise
        return wrapper
    return decorator

class SecurityHeaders:
    """Middleware untuk menambahkan security headers"""
    
    @staticmethod
    def add_security_headers(response):
        """Add security headers to response"""
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response

def validate_user_access(resource_user_id: int):
    """Middleware untuk validasi akses user ke resource"""
    def dependency(current_user: User = Depends(get_current_user)):
        # Admin bisa akses semua resource
        if current_user.is_admin:
            return current_user
        
        # User biasa hanya bisa akses resource miliknya sendiri
        if current_user.id != resource_user_id:
            raise HTTPException(
                status_code=403,
                detail="Anda tidak memiliki akses ke resource ini."
            )
        
        return current_user
    
    return dependency

class IPWhitelist:
    """Middleware untuk IP whitelisting (untuk admin endpoints)"""
    
    def __init__(self, allowed_ips: list = None):
        self.allowed_ips = allowed_ips or []
    
    def __call__(self, request):
        """Check if IP is whitelisted"""
        if not self.allowed_ips:
            return True  # No restriction if no IPs specified
        
        client_ip = request.client.host
        
        # Check if IP is in whitelist
        for allowed_ip in self.allowed_ips:
            if client_ip == allowed_ip or client_ip.startswith(allowed_ip):
                return True
        
        return False

# Instance untuk production (bisa dikonfigurasi via environment)
admin_ip_whitelist = IPWhitelist([
    "127.0.0.1",
    "::1",
    "10.0.0.",  # Internal network
    "192.168."  # Local network
])

class SecurityMiddleware:
    """Security middleware untuk FastAPI"""
    
    def __init__(self, app, csrf_protection: bool = True, security_headers: bool = True, max_request_size: int = 10 * 1024 * 1024):
        self.app = app
        self.csrf_protection = csrf_protection
        self.security_headers = security_headers
        self.max_request_size = max_request_size
    
    async def __call__(self, scope, receive, send):
        """ASGI middleware implementation"""
        if scope["type"] == "http":
            # Add security processing here
            pass
        
        await self.app(scope, receive, send)
