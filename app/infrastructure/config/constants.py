"""
Constants untuk aplikasi FA
"""

class RateLimits:
    """Rate limiting constants"""
    DEFAULT_REQUESTS_PER_MINUTE = 60
    AUTH_REQUESTS_PER_MINUTE = 10
    API_REQUESTS_PER_MINUTE = 100
    ADMIN_REQUESTS_PER_MINUTE = 200
    PPOB_REQUESTS_PER_MINUTE = 120
    
    # Burst limits
    AUTH_BURST_LIMIT = 5
    API_BURST_LIMIT = 50
    ADMIN_BURST_LIMIT = 100
    PPOB_BURST_LIMIT = 60

class StatusMessages:
    """Status message constants"""
    SUCCESS = "success"
    ERROR = "error"
    PENDING = "pending"
    FAILED = "failed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RATE_LIMIT_EXCEEDED = "Rate limit exceeded. Please try again later."

class ErrorCodes:
    """Error code constants"""
    VALIDATION_ERROR = "VALIDATION_ERROR"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    AUTHORIZATION_ERROR = "AUTHORIZATION_ERROR"
    NOT_FOUND_ERROR = "NOT_FOUND_ERROR"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    RATE_LIMIT_ERROR = "RATE_LIMIT_ERROR"

class CacheKeys:
    """Cache key constants"""
    USER_PREFIX = "user:"
    PRODUCT_PREFIX = "product:"
    TRANSACTION_PREFIX = "transaction:"
    PPOB_PREFIX = "ppob:"
    ADMIN_PREFIX = "admin:"

class DatabaseConstants:
    """Database related constants"""
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    DEFAULT_TIMEOUT = 30
