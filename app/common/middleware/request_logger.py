"""
Request Logging Middleware untuk mencatat semua request dan response
Memberikan visibility penuh terhadap traffic API dan error yang terjadi
"""

import time
import json
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse

logger = logging.getLogger("request_logger")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware untuk logging semua HTTP requests dan responses
    Memberikan insight lengkap tentang API traffic dan performance
    """
    
    def __init__(self, app, log_body: bool = False, log_headers: bool = True):
        super().__init__(app)
        self.log_body = log_body
        self.log_headers = log_headers
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request dan log informasi penting"""
        
        # Record start time
        start_time = time.time()
        
        # Generate request ID untuk tracking
        import uuid
        request_id = str(uuid.uuid4())[:8]
        
        # Log incoming request
        await self._log_request(request, request_id)
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log response
            await self._log_response(request, response, request_id, process_time)
            
            return response
            
        except Exception as exc:
            # Log exception
            process_time = time.time() - start_time
            await self._log_exception(request, exc, request_id, process_time)
            raise
    
    async def _log_request(self, request: Request, request_id: str):
        """Log incoming request details"""
        
        # Basic request info
        log_data = {
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_ip": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent", "N/A")
        }
        
        # Add headers if enabled
        if self.log_headers:
            # Filter sensitive headers
            safe_headers = {
                k: v for k, v in request.headers.items() 
                if k.lower() not in ["authorization", "cookie", "x-api-key"]
            }
            log_data["headers"] = safe_headers
        
        # Add body for POST/PUT/PATCH if enabled
        if self.log_body and request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    # Try to parse as JSON, fallback to string
                    try:
                        log_data["body"] = json.loads(body.decode())
                    except:
                        log_data["body"] = body.decode()[:500]  # Limit body size
            except:
                log_data["body"] = "Could not read body"
        
        logger.info(
            f"🔵 INCOMING REQUEST [{request_id}] {request.method} {request.url.path}",
            extra={"request_data": log_data}
        )
    
    async def _log_response(self, request: Request, response: Response, request_id: str, process_time: float):
        """Log response details"""
        
        log_data = {
            "request_id": request_id,
            "status_code": response.status_code,
            "process_time_ms": round(process_time * 1000, 2),
            "response_headers": dict(response.headers) if self.log_headers else {}
        }
        
        # Determine log level based on status code
        if response.status_code < 400:
            log_level = "info"
            emoji = "🟢"
        elif response.status_code < 500:
            log_level = "warning"
            emoji = "🟡"
        else:
            log_level = "error"
            emoji = "🔴"
        
        getattr(logger, log_level)(
            f"{emoji} RESPONSE [{request_id}] {response.status_code} {request.method} {request.url.path} ({process_time*1000:.2f}ms)",
            extra={"response_data": log_data}
        )
    
    async def _log_exception(self, request: Request, exc: Exception, request_id: str, process_time: float):
        """Log exception during request processing"""
        
        log_data = {
            "request_id": request_id,
            "exception_type": exc.__class__.__name__,
            "exception_message": str(exc),
            "process_time_ms": round(process_time * 1000, 2),
            "method": request.method,
            "path": request.url.path
        }
        
        logger.error(
            f"💥 EXCEPTION [{request_id}] {exc.__class__.__name__}: {str(exc)} - {request.method} {request.url.path}",
            extra={"exception_data": log_data}
        )
    
    def _get_client_ip(self, request: Request) -> str:
        """Get real client IP address"""
        # Check for forwarded headers first
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"


class EndpointLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware khusus untuk logging endpoint-specific information
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log endpoint-specific information"""
        
        # Log endpoint access
        endpoint_logger = logging.getLogger(f"endpoint.{request.url.path.replace('/', '.')}")
        
        endpoint_logger.info(
            f"Accessing endpoint: {request.method} {request.url.path}",
            extra={
                "endpoint": request.url.path,
                "method": request.method,
                "client_ip": self._get_client_ip(request)
            }
        )
        
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            endpoint_logger.error(
                f"Error in endpoint {request.url.path}: {exc.__class__.__name__}: {str(exc)}",
                extra={
                    "endpoint": request.url.path,
                    "error_type": exc.__class__.__name__,
                    "error_message": str(exc)
                }
            )
            raise
    
    def _get_client_ip(self, request: Request) -> str:
        """Get real client IP address"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
