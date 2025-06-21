# Rate Limiting Core untuk Discord Bot Operations
from fastapi import Request
from typing import Dict
import time
from collections import defaultdict, deque

class RateLimiter:
    def __init__(self):
        # Storage untuk tracking requests per IP/user
        self.requests: Dict[str, deque] = defaultdict(deque)
        # Konfigurasi rate limits
        self.limits = {
            "bot_operations": {"max_requests": 10, "window": 60},  # 10 req/menit
            "bulk_operations": {"max_requests": 5, "window": 300}, # 5 req/5menit
            "messaging": {"max_requests": 20, "window": 60}        # 20 msg/menit
        }
    
    def _get_client_id(self, request: Request) -> str:
        """Dapatkan identifier unik untuk client"""
        # Prioritas: user_id dari auth > IP address
        user_id = getattr(request.state, 'user_id', None)
        return user_id or request.client.host
    
    def _cleanup_old_requests(self, client_id: str, window: int):
        """Bersihkan request lama yang sudah di luar window"""
        current_time = time.time()
        client_requests = self.requests[client_id]
        
        while client_requests and client_requests[0] < current_time - window:
            client_requests.popleft()
    
    def check_rate_limit(self, request: Request, operation_type: str) -> bool:
        """Cek apakah request melebihi rate limit"""
        if operation_type not in self.limits:
            return True
        
        client_id = self._get_client_id(request)
        limit_config = self.limits[operation_type]
        current_time = time.time()
        
        # Cleanup request lama
        self._cleanup_old_requests(client_id, limit_config["window"])
        
        # Cek apakah sudah melebihi limit
        if len(self.requests[client_id]) >= limit_config["max_requests"]:
            return False
        
        # Tambah request baru
        self.requests[client_id].append(current_time)
        return True

# Instance global
rate_limiter = RateLimiter()
