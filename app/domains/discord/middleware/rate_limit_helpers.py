# Rate Limiter Helper Functions
from fastapi import HTTPException, Request, status
from .rate_limiter import rate_limiter

def get_remaining_requests(request: Request, operation_type: str) -> int:
    """Dapatkan sisa request yang bisa dilakukan"""
    if operation_type not in rate_limiter.limits:
        return 999
    
    client_id = rate_limiter._get_client_id(request)
    limit_config = rate_limiter.limits[operation_type]
    
    rate_limiter._cleanup_old_requests(client_id, limit_config["window"])
    return max(0, limit_config["max_requests"] - len(rate_limiter.requests[client_id]))

def rate_limit_middleware(operation_type: str):
    """Decorator untuk rate limiting"""
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            if not rate_limiter.check_rate_limit(request, operation_type):
                remaining = get_remaining_requests(request, operation_type)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Sisa: {remaining} requests",
                    headers={"Retry-After": "60"}
                )
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator

def check_bot_operation_limit(request: Request) -> bool:
    """Cek rate limit untuk bot operations"""
    return rate_limiter.check_rate_limit(request, "bot_operations")

def check_bulk_operation_limit(request: Request) -> bool:
    """Cek rate limit untuk bulk operations"""
    return rate_limiter.check_rate_limit(request, "bulk_operations")

def check_messaging_limit(request: Request) -> bool:
    """Cek rate limit untuk messaging"""
    return rate_limiter.check_rate_limit(request, "messaging")

def get_rate_limit_status(request: Request) -> dict:
    """Dapatkan status rate limit untuk semua operasi"""
    return {
        "bot_operations": get_remaining_requests(request, "bot_operations"),
        "bulk_operations": get_remaining_requests(request, "bulk_operations"),
        "messaging": get_remaining_requests(request, "messaging")
    }
