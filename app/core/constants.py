"""
Konstanta aplikasi untuk menghindari magic numbers dan strings (DRY principle)
"""

# Rate Limiting Constants
class RateLimits:
    # Requests per minute
    AUTH_REQUESTS_PER_MINUTE = 5
    API_REQUESTS_PER_MINUTE = 60
    PPOB_REQUESTS_PER_MINUTE = 30
    ADMIN_REQUESTS_PER_MINUTE = 100
    
    # Burst limits
    AUTH_BURST_LIMIT = 10
    API_BURST_LIMIT = 120
    PPOB_BURST_LIMIT = 60
    ADMIN_BURST_LIMIT = 200

# HTTP Status Messages
class StatusMessages:
    SUCCESS = "Operasi berhasil"
    CREATED = "Data berhasil dibuat"
    UPDATED = "Data berhasil diperbarui"
    DELETED = "Data berhasil dihapus"
    NOT_FOUND = "Data tidak ditemukan"
    UNAUTHORIZED = "Tidak memiliki akses"
    FORBIDDEN = "Akses ditolak"
    VALIDATION_ERROR = "Data tidak valid"
    RATE_LIMIT_EXCEEDED = "Terlalu banyak permintaan, coba lagi nanti"
    INTERNAL_ERROR = "Terjadi kesalahan internal"

# Cache Keys
class CacheKeys:
    USER_PROFILE = "user_profile:{user_id}"
    WALLET_BALANCE = "wallet_balance:{user_id}"
    PPOB_PRODUCTS = "ppob_products:{category}"
    ADMIN_SESSION = "admin_session:{admin_id}"
    RATE_LIMIT = "rate_limit:{endpoint}:{identifier}"

# Database Constants
class DatabaseConstants:
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    DEFAULT_TIMEOUT = 30

# File Upload Constants
class FileConstants:
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.pdf', '.doc', '.docx'}
    UPLOAD_PATH = "uploads"

# Transaction Constants
class TransactionConstants:
    MIN_AMOUNT = 1000
    MAX_AMOUNT = 10000000
    PENDING_TIMEOUT_MINUTES = 15
    
# PPOB Constants
class PPOBConstants:
    TIMEOUT_SECONDS = 30
    RETRY_ATTEMPTS = 3
    RETRY_DELAY = 1
