"""
Rate Limiter Middleware untuk implementasi rate limiting
Single Responsibility: Menangani pembatasan request rate
"""

import time
import asyncio
from typing import Dict, Optional, Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.config.constants import RateLimits, StatusMessages
from app.infrastructure.config.settings import settings
import logging

logger = logging.getLogger(__name__)


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    Rate limiter middleware dengan sliding window algorithm
    Menggunakan in-memory storage untuk simplicity
    Untuk production, gunakan Redis atau database
    """
    
    def __init__(self, app):
        super().__init__(app)
        # In-memory storage untuk rate limiting
        # Format: {key: {"count": int, "window_start": float, "requests": [timestamps]}}
        self._storage: Dict[str, Dict] = {}
        self._cleanup_interval = 60  # Cleanup every minute
        self._last_cleanup = time.time()
        
        # Rate limit configurations per endpoint pattern
        self._rate_configs = {
            "/api/v1/auth/": {
                "requests_per_minute": RateLimits.AUTH_REQUESTS_PER_MINUTE,
                "burst_limit": RateLimits.AUTH_BURST_LIMIT
            },
            "/api/v1/ppob/": {
                "requests_per_minute": RateLimits.PPOB_REQUESTS_PER_MINUTE,
                "burst_limit": RateLimits.PPOB_BURST_LIMIT
            },
            "/api/v1/admin/": {
                "requests_per_minute": RateLimits.ADMIN_REQUESTS_PER_MINUTE,
                "burst_limit": RateLimits.ADMIN_BURST_LIMIT
            },
            "default": {
                "requests_per_minute": RateLimits.API_REQUESTS_PER_MINUTE,
                "burst_limit": RateLimits.API_BURST_LIMIT
            }
        }
    
    async def dispatch(self, request: Request, call_next):
        """Main rate limiting logic"""
        try:
            # Skip rate limiting untuk health checks dan docs
            if self._should_skip_rate_limiting(request):
                return await call_next(request)
            
            # Generate rate limit key
            rate_key = self._generate_rate_key(request)
            
            # Get rate limit config untuk endpoint
            config = self._get_rate_config(request.url.path)
            
            # Check rate limit
            is_allowed, retry_after = await self._check_rate_limit(
                rate_key, 
                config["requests_per_minute"],
                config["burst_limit"]
            )
            
            if not is_allowed:
                return self._create_rate_limit_response(retry_after)
            
            # Process request
            response = await call_next(request)
            
            # Add rate limit headers
            self._add_rate_limit_headers(response, rate_key, config)
            
            # Cleanup old entries periodically
            await self._periodic_cleanup()
            
            return response
            
        except Exception as e:
            logger.error(f"Error in rate limiter middleware: {e}")
            # Jangan blokir request jika rate limiter error
            return await call_next(request)
    
    def _should_skip_rate_limiting(self, request: Request) -> bool:
        """Check apakah request harus di-skip dari rate limiting"""
        skip_paths = [
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/favicon.ico"
        ]
        
        return any(request.url.path.startswith(path) for path in skip_paths)
    
    def _generate_rate_key(self, request: Request) -> str:
        """Generate unique key untuk rate limiting"""
        # Kombinasi IP address dan user ID (jika ada)
        client_ip = self._get_client_ip(request)
        
        # Try to get user ID dari token atau session
        user_id = self._extract_user_id(request)
        
        if user_id:
            return f"rate_limit:user:{user_id}"
        else:
            return f"rate_limit:ip:{client_ip}"
    
    def _get_client_ip(self, request: Request) -> str:
        """Get real client IP"""
        # Check X-Forwarded-For header
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        # Check X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback ke client host
        return request.client.host if request.client else "unknown"
    
    def _extract_user_id(self, request: Request) -> Optional[str]:
        """Extract user ID dari request untuk user-specific rate limiting"""
        try:
            # Try to get dari Authorization header
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                # Dalam implementasi nyata, decode JWT token untuk get user ID
                # Untuk sekarang, return None untuk menggunakan IP-based limiting
                pass
            
            return None
            
        except Exception:
            return None
    
    def _get_rate_config(self, path: str) -> Dict[str, int]:
        """Get rate limit configuration untuk path tertentu"""
        for pattern, config in self._rate_configs.items():
            if pattern != "default" and path.startswith(pattern):
                return config
        
        return self._rate_configs["default"]
    
    async def _check_rate_limit(
        self, 
        key: str, 
        requests_per_minute: int, 
        burst_limit: int
    ) -> tuple[bool, int]:
        """
        Check rate limit menggunakan sliding window algorithm
        
        Returns:
            (is_allowed, retry_after_seconds)
        """
        current_time = time.time()
        window_size = 60  # 1 minute window
        
        # Get atau create entry
        if key not in self._storage:
            self._storage[key] = {
                "requests": [],
                "window_start": current_time
            }
        
        entry = self._storage[key]
        
        # Remove old requests (outside window)
        entry["requests"] = [
            req_time for req_time in entry["requests"]
            if current_time - req_time < window_size
        ]
        
        # Check burst limit (requests dalam 10 detik terakhir)
        recent_requests = [
            req_time for req_time in entry["requests"]
            if current_time - req_time < 10
        ]
        
        if len(recent_requests) >= burst_limit:
            retry_after = 10 - (current_time - min(recent_requests))
            return False, max(1, int(retry_after))
        
        # Check rate limit (requests per minute)
        if len(entry["requests"]) >= requests_per_minute:
            # Calculate retry after berdasarkan oldest request dalam window
            oldest_request = min(entry["requests"])
            retry_after = window_size - (current_time - oldest_request)
            return False, max(1, int(retry_after))
        
        # Allow request dan record timestamp
        entry["requests"].append(current_time)
        
        return True, 0
    
    def _create_rate_limit_response(self, retry_after: int) -> JSONResponse:
        """Create rate limit exceeded response"""
        return JSONResponse(
            status_code=429,
            content={
                "success": False,
                "message": StatusMessages.RATE_LIMIT_EXCEEDED,
                "error_code": "RATE_LIMIT_EXCEEDED",
                "retry_after": retry_after
            },
            headers={
                "Retry-After": str(retry_after),
                "X-RateLimit-Limit": "60",
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(time.time() + retry_after))
            }
        )
    
    def _add_rate_limit_headers(self, response: Response, key: str, config: Dict[str, int]):
        """Add rate limit headers ke response"""
        try:
            if key in self._storage:
                entry = self._storage[key]
                current_time = time.time()
                
                # Count requests dalam current window
                current_requests = len([
                    req_time for req_time in entry["requests"]
                    if current_time - req_time < 60
                ])
                
                remaining = max(0, config["requests_per_minute"] - current_requests)
                reset_time = int(current_time + 60)
                
                response.headers["X-RateLimit-Limit"] = str(config["requests_per_minute"])
                response.headers["X-RateLimit-Remaining"] = str(remaining)
                response.headers["X-RateLimit-Reset"] = str(reset_time)
                
        except Exception as e:
            logger.warning(f"Error adding rate limit headers: {e}")
    
    async def _periodic_cleanup(self):
        """Cleanup old entries untuk prevent memory leak"""
        current_time = time.time()
        
        if current_time - self._last_cleanup < self._cleanup_interval:
            return
        
        try:
            # Remove entries yang sudah tidak aktif > 5 menit
            cleanup_threshold = current_time - 300  # 5 minutes
            
            keys_to_remove = []
            for key, entry in self._storage.items():
                if not entry["requests"]:
                    keys_to_remove.append(key)
                    continue
                
                # Remove old requests
                entry["requests"] = [
                    req_time for req_time in entry["requests"]
                    if req_time > cleanup_threshold
                ]
                
                # Remove entry jika tidak ada requests
                if not entry["requests"]:
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del self._storage[key]
            
            self._last_cleanup = current_time
            
            if keys_to_remove:
                logger.debug(f"Cleaned up {len(keys_to_remove)} rate limit entries")
                
        except Exception as e:
            logger.error(f"Error during rate limit cleanup: {e}")
    
    def get_stats(self) -> Dict[str, any]:
        """Get rate limiter statistics untuk monitoring"""
        current_time = time.time()
        active_keys = 0
        total_requests = 0
        
        for entry in self._storage.values():
            if entry["requests"]:
                # Count requests dalam last 5 minutes
                recent_requests = [
                    req_time for req_time in entry["requests"]
                    if current_time - req_time < 300
                ]
                if recent_requests:
                    active_keys += 1
                    total_requests += len(recent_requests)
        
        return {
            "active_keys": active_keys,
            "total_requests_last_5min": total_requests,
            "storage_size": len(self._storage),
            "last_cleanup": self._last_cleanup
        }
