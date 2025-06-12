"""
Security Middleware untuk implementasi keamanan aplikasi
Single Responsibility: Menangani aspek keamanan HTTP requests
"""

import time
import hashlib
import hmac
from typing import Optional, List, Dict, Any
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.constants import StatusMessages
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Middleware untuk menangani berbagai aspek keamanan:
    - CSRF Protection
    - Request signing verification
    - Security headers
    - IP whitelisting/blacklisting
    """
    
    def __init__(
        self, 
        app,
        csrf_protection: bool = True,
        security_headers: bool = True,
        ip_whitelist: Optional[List[str]] = None,
        ip_blacklist: Optional[List[str]] = None,
        max_request_size: int = 10 * 1024 * 1024  # 10MB
    ):
        super().__init__(app)
        self.csrf_protection = csrf_protection
        self.security_headers = security_headers
        self.ip_whitelist = ip_whitelist or []
        self.ip_blacklist = ip_blacklist or []
        self.max_request_size = max_request_size
        
        # Security headers configuration
        self.security_headers_config = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
        }
    
    async def dispatch(self, request: Request, call_next):
        """Main security middleware logic"""
        try:
            # 1. Check IP whitelist/blacklist
            if not await self._check_ip_access(request):
                return self._create_forbidden_response("IP tidak diizinkan")
            
            # 2. Check request size
            if not await self._check_request_size(request):
                return self._create_bad_request_response("Request terlalu besar")
            
            # 3. Validate request signature (untuk API tertentu)
            if not await self._validate_request_signature(request):
                return self._create_unauthorized_response("Signature tidak valid")
            
            # 4. CSRF Protection
            if self.csrf_protection and not await self._check_csrf_token(request):
                return self._create_forbidden_response("CSRF token tidak valid")
            
            # 5. Check for suspicious patterns
            if await self._detect_suspicious_patterns(request):
                logger.warning(f"Suspicious request detected from {self._get_client_ip(request)}")
                return self._create_forbidden_response("Request mencurigakan")
            
            # Process request
            response = await call_next(request)
            
            # 6. Add security headers
            if self.security_headers:
                self._add_security_headers(response)
            
            # 7. Log security events
            await self._log_security_event(request, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error in security middleware: {e}")
            # Jangan blokir request jika ada error di middleware
            return await call_next(request)
    
    async def _check_ip_access(self, request: Request) -> bool:
        """Check IP whitelist dan blacklist"""
        client_ip = self._get_client_ip(request)
        
        # Check blacklist first
        if self.ip_blacklist and client_ip in self.ip_blacklist:
            logger.warning(f"Blocked IP from blacklist: {client_ip}")
            return False
        
        # Check whitelist (jika ada)
        if self.ip_whitelist and client_ip not in self.ip_whitelist:
            logger.warning(f"IP not in whitelist: {client_ip}")
            return False
        
        return True
    
    async def _check_request_size(self, request: Request) -> bool:
        """Check ukuran request"""
        try:
            content_length = request.headers.get('content-length')
            if content_length and int(content_length) > self.max_request_size:
                return False
            return True
        except (ValueError, TypeError):
            return True
    
    async def _validate_request_signature(self, request: Request) -> bool:
        """Validate request signature untuk API yang memerlukan"""
        # Skip untuk endpoint yang tidak memerlukan signature
        if not self._requires_signature(request):
            return True
        
        try:
            # Get signature dari header
            signature = request.headers.get('X-Signature')
            timestamp = request.headers.get('X-Timestamp')
            
            if not signature or not timestamp:
                return False
            
            # Check timestamp (prevent replay attacks)
            current_time = int(time.time())
            request_time = int(timestamp)
            
            # Allow 5 minutes tolerance
            if abs(current_time - request_time) > 300:
                logger.warning(f"Request timestamp too old: {timestamp}")
                return False
            
            # Validate signature
            body = await self._get_request_body(request)
            expected_signature = self._generate_signature(
                method=request.method,
                path=request.url.path,
                timestamp=timestamp,
                body=body
            )
            
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            logger.error(f"Error validating signature: {e}")
            return False
    
    async def _check_csrf_token(self, request: Request) -> bool:
        """Check CSRF token untuk state-changing operations"""
        # Skip untuk GET, HEAD, OPTIONS
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        # Skip untuk API endpoints (menggunakan token auth)
        if request.url.path.startswith('/api/'):
            return True
        
        try:
            # Get CSRF token dari header atau form
            csrf_token = (
                request.headers.get('X-CSRF-Token') or
                request.headers.get('X-CSRFToken')
            )
            
            if not csrf_token:
                # Try to get from form data
                if request.headers.get('content-type', '').startswith('application/x-www-form-urlencoded'):
                    form = await request.form()
                    csrf_token = form.get('csrf_token')
            
            if not csrf_token:
                return False
            
            # Validate CSRF token
            return self._validate_csrf_token(csrf_token, request)
            
        except Exception as e:
            logger.error(f"Error checking CSRF token: {e}")
            return False
    
    async def _detect_suspicious_patterns(self, request: Request) -> bool:
        """Detect pola request yang mencurigakan"""
        try:
            # Check untuk SQL injection patterns
            suspicious_patterns = [
                'union select', 'drop table', 'delete from',
                'insert into', 'update set', '--', '/*', '*/',
                '<script', 'javascript:', 'vbscript:', 'onload=',
                'onerror=', 'eval(', 'alert(', 'document.cookie'
            ]
            
            # Check URL path
            path_lower = request.url.path.lower()
            query_lower = str(request.url.query).lower()
            
            for pattern in suspicious_patterns:
                if pattern in path_lower or pattern in query_lower:
                    return True
            
            # Check headers untuk suspicious values
            user_agent = request.headers.get('user-agent', '').lower()
            suspicious_agents = ['sqlmap', 'nikto', 'nmap', 'masscan', 'zap']
            
            for agent in suspicious_agents:
                if agent in user_agent:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error detecting suspicious patterns: {e}")
            return False
    
    def _add_security_headers(self, response: Response) -> None:
        """Add security headers ke response"""
        for header, value in self.security_headers_config.items():
            response.headers[header] = value
    
    async def _log_security_event(self, request: Request, response: Response) -> None:
        """Log security events"""
        # Log hanya untuk event penting
        if response.status_code in [401, 403, 429]:
            logger.warning(
                f"Security event: {response.status_code} - "
                f"{request.method} {request.url.path} - "
                f"IP: {self._get_client_ip(request)} - "
                f"User-Agent: {request.headers.get('user-agent', 'N/A')}"
            )
    
    def _get_client_ip(self, request: Request) -> str:
        """Get real client IP"""
        # Check X-Forwarded-For header
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        
        # Check X-Real-IP header
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip
        
        # Fallback ke client host
        return request.client.host if request.client else 'unknown'
    
    def _requires_signature(self, request: Request) -> bool:
        """Check apakah endpoint memerlukan signature"""
        # Endpoint yang memerlukan signature
        signature_required_paths = [
            '/api/v1/ppob/',
            '/api/v1/transaction/callback',
            '/api/v1/admin/sensitive'
        ]
        
        return any(request.url.path.startswith(path) for path in signature_required_paths)
    
    async def _get_request_body(self, request: Request) -> bytes:
        """Get request body untuk signature validation"""
        try:
            # Hati-hati: body hanya bisa dibaca sekali
            # Perlu implementasi khusus jika body sudah dibaca
            return await request.body()
        except Exception:
            return b''
    
    def _generate_signature(self, method: str, path: str, timestamp: str, body: bytes) -> str:
        """Generate expected signature"""
        # Create string to sign
        string_to_sign = f"{method}\n{path}\n{timestamp}\n{body.decode('utf-8', errors='ignore')}"
        
        # Generate HMAC signature
        signature = hmac.new(
            settings.SECRET_KEY.encode(),
            string_to_sign.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def _validate_csrf_token(self, token: str, request: Request) -> bool:
        """Validate CSRF token"""
        try:
            # Simple CSRF token validation
            # Dalam implementasi production, gunakan cryptographic token
            expected_token = hashlib.sha256(
                f"{settings.SECRET_KEY}{self._get_client_ip(request)}".encode()
            ).hexdigest()[:32]
            
            return hmac.compare_digest(token, expected_token)
            
        except Exception:
            return False
    
    def _create_forbidden_response(self, message: str) -> JSONResponse:
        """Create 403 Forbidden response"""
        return JSONResponse(
            status_code=403,
            content={
                "success": False,
                "message": message,
                "error_code": "FORBIDDEN"
            }
        )
    
    def _create_unauthorized_response(self, message: str) -> JSONResponse:
        """Create 401 Unauthorized response"""
        return JSONResponse(
            status_code=401,
            content={
                "success": False,
                "message": message,
                "error_code": "UNAUTHORIZED"
            }
        )
    
    def _create_bad_request_response(self, message: str) -> JSONResponse:
        """Create 400 Bad Request response"""
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": message,
                "error_code": "BAD_REQUEST"
            }
        )
