"""
Global Error Handler Middleware untuk implementasi Open/Closed Principle
Menangani semua exceptions secara terpusat dan konsisten
"""

import traceback
import uuid
from typing import Dict, Any, Optional, Type
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from pydantic import ValidationError
from app.infrastructure.config.constants import StatusMessages
from app.common.exceptions.custom_exceptions import (
    BaseCustomException, ValidationException, NotFoundError,
    UnauthorizedError, ForbiddenError, ConflictError, InternalServerError
)
import logging

logger = logging.getLogger(__name__)
module_logger = logging.getLogger("module_import")


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Global error handler middleware
    Open/Closed Principle: Mudah diperluas untuk handle exception types baru
    """
    
    def __init__(self, app, debug: bool = False):
        super().__init__(app)
        self.debug = debug
        self.error_handlers = self._setup_error_handlers()
    
    def _setup_error_handlers(self) -> Dict[Type[Exception], callable]:
        """Setup mapping exception types ke handler functions"""
        return {
            HTTPException: self._handle_http_exception,
            ValidationError: self._handle_validation_error,
            SQLAlchemyError: self._handle_database_error,
            IntegrityError: self._handle_integrity_error,
            BaseCustomException: self._handle_custom_exception,
            ValidationException: self._handle_validation_exception,
            NotFoundError: self._handle_not_found_error,
            UnauthorizedError: self._handle_unauthorized_error,
            ForbiddenError: self._handle_forbidden_error,
            ConflictError: self._handle_conflict_error,
            ModuleNotFoundError: self._handle_module_not_found_error,
            ImportError: self._handle_import_error,
            ValueError: self._handle_value_error,
            KeyError: self._handle_key_error,
            AttributeError: self._handle_attribute_error,
            TypeError: self._handle_type_error,
            Exception: self._handle_generic_exception
        }
    
    async def dispatch(self, request: Request, call_next):
        """Main error handling logic"""
        try:
            response = await call_next(request)
            return response
            
        except Exception as exc:
            # Generate unique error ID untuk tracking
            error_id = str(uuid.uuid4())
            
            # Log error dengan context
            await self._log_error(exc, request, error_id)
            
            # Handle error berdasarkan type
            return await self._handle_error(exc, request, error_id)
    
    async def _handle_error(self, exc: Exception, request: Request, error_id: str) -> JSONResponse:
        """Route error ke handler yang sesuai"""
        # Cari handler yang paling spesifik
        for exc_type, handler in self.error_handlers.items():
            if isinstance(exc, exc_type):
                return await handler(exc, request, error_id)
        
        # Fallback ke generic handler
        return await self._handle_generic_exception(exc, request, error_id)
    
    async def _handle_http_exception(self, exc: HTTPException, request: Request, error_id: str) -> JSONResponse:
        """Handle FastAPI HTTPException"""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": exc.detail,
                "error_code": f"HTTP_{exc.status_code}",
                "error_id": error_id if self.debug else None
            }
        )
    
    async def _handle_validation_error(self, exc: ValidationError, request: Request, error_id: str) -> JSONResponse:
        """Handle Pydantic ValidationError"""
        errors = []
        for error in exc.errors():
            field = " -> ".join(str(x) for x in error["loc"])
            message = error["msg"]
            errors.append(f"{field}: {message}")
        
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "message": StatusMessages.VALIDATION_ERROR,
                "errors": errors,
                "error_code": "VALIDATION_ERROR",
                "error_id": error_id if self.debug else None
            }
        )
    
    async def _handle_database_error(self, exc: SQLAlchemyError, request: Request, error_id: str) -> JSONResponse:
        """Handle SQLAlchemy database errors"""
        # Jangan expose database error details ke client
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Terjadi kesalahan database",
                "error_code": "DATABASE_ERROR",
                "error_id": error_id if self.debug else None
            }
        )
    
    async def _handle_integrity_error(self, exc: IntegrityError, request: Request, error_id: str) -> JSONResponse:
        """Handle database integrity constraint errors"""
        # Parse constraint error untuk user-friendly message
        message = self._parse_integrity_error(exc)
        
        return JSONResponse(
            status_code=409,
            content={
                "success": False,
                "message": message,
                "error_code": "INTEGRITY_ERROR",
                "error_id": error_id if self.debug else None
            }
        )
    
    async def _handle_custom_exception(self, exc: BaseCustomException, request: Request, error_id: str) -> JSONResponse:
        """Handle custom application exceptions"""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": exc.message,
                "error_code": exc.error_code,
                "details": exc.details if self.debug else None,
                "error_id": error_id if self.debug else None
            }
        )
    
    async def _handle_validation_exception(self, exc: ValidationException, request: Request, error_id: str) -> JSONResponse:
        """Handle custom validation exceptions"""
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": exc.message,
                "errors": exc.errors,
                "error_code": "VALIDATION_ERROR",
                "error_id": error_id if self.debug else None
            }
        )
    
    async def _handle_not_found_error(self, exc: NotFoundError, request: Request, error_id: str) -> JSONResponse:
        """Handle not found errors"""
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "message": exc.message or StatusMessages.NOT_FOUND,
                "error_code": "NOT_FOUND",
                "error_id": error_id if self.debug else None
            }
        )
    
    async def _handle_unauthorized_error(self, exc: UnauthorizedError, request: Request, error_id: str) -> JSONResponse:
        """Handle unauthorized errors"""
        return JSONResponse(
            status_code=401,
            content={
                "success": False,
                "message": exc.message or StatusMessages.UNAUTHORIZED,
                "error_code": "UNAUTHORIZED",
                "error_id": error_id if self.debug else None
            }
        )
    
    async def _handle_forbidden_error(self, exc: ForbiddenError, request: Request, error_id: str) -> JSONResponse:
        """Handle forbidden errors"""
        return JSONResponse(
            status_code=403,
            content={
                "success": False,
                "message": exc.message or StatusMessages.FORBIDDEN,
                "error_code": "FORBIDDEN",
                "error_id": error_id if self.debug else None
            }
        )
    
    async def _handle_conflict_error(self, exc: ConflictError, request: Request, error_id: str) -> JSONResponse:
        """Handle conflict errors"""
        return JSONResponse(
            status_code=409,
            content={
                "success": False,
                "message": exc.message,
                "error_code": "CONFLICT",
                "error_id": error_id if self.debug else None
            }
        )
    
    async def _handle_value_error(self, exc: ValueError, request: Request, error_id: str) -> JSONResponse:
        """Handle ValueError"""
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": "Data tidak valid",
                "error_code": "INVALID_VALUE",
                "error_id": error_id if self.debug else None
            }
        )
    
    async def _handle_key_error(self, exc: KeyError, request: Request, error_id: str) -> JSONResponse:
        """Handle KeyError"""
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": f"Field yang diperlukan tidak ditemukan: {str(exc)}",
                "error_code": "MISSING_FIELD",
                "error_id": error_id if self.debug else None
            }
        )
    
    async def _handle_attribute_error(self, exc: AttributeError, request: Request, error_id: str) -> JSONResponse:
        """Handle AttributeError"""
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": StatusMessages.INTERNAL_ERROR,
                "error_code": "ATTRIBUTE_ERROR",
                "error_id": error_id if self.debug else None
            }
        )
    
    async def _handle_module_not_found_error(self, exc: ModuleNotFoundError, request: Request, error_id: str) -> JSONResponse:
        """Handle ModuleNotFoundError"""
        # Log detailed module error
        module_logger.error(
            f"🚫 MODULE NOT FOUND [{error_id}]: {str(exc)} - {request.method} {request.url.path}",
            extra={
                "error_context": {
                    "error_id": error_id,
                    "module_error": str(exc),
                    "endpoint": request.url.path,
                    "method": request.method,
                    "traceback": traceback.format_exc()
                }
            }
        )
        
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Module tidak ditemukan - terjadi kesalahan konfigurasi sistem",
                "error_code": "MODULE_NOT_FOUND",
                "error_id": error_id if self.debug else None,
                "details": str(exc) if self.debug else None
            }
        )
    
    async def _handle_import_error(self, exc: ImportError, request: Request, error_id: str) -> JSONResponse:
        """Handle ImportError"""
        # Log detailed import error
        module_logger.error(
            f"🚫 IMPORT ERROR [{error_id}]: {str(exc)} - {request.method} {request.url.path}",
            extra={
                "error_context": {
                    "error_id": error_id,
                    "import_error": str(exc),
                    "endpoint": request.url.path,
                    "method": request.method,
                    "traceback": traceback.format_exc()
                }
            }
        )
        
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Gagal mengimpor module - terjadi kesalahan konfigurasi sistem",
                "error_code": "IMPORT_ERROR",
                "error_id": error_id if self.debug else None,
                "details": str(exc) if self.debug else None
            }
        )
    
    async def _handle_type_error(self, exc: TypeError, request: Request, error_id: str) -> JSONResponse:
        """Handle TypeError"""
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": "Tipe data tidak sesuai",
                "error_code": "TYPE_ERROR",
                "error_id": error_id if self.debug else None
            }
        )
    
    async def _handle_generic_exception(self, exc: Exception, request: Request, error_id: str) -> JSONResponse:
        """Handle semua exception yang tidak ter-handle"""
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": StatusMessages.INTERNAL_ERROR,
                "error_code": "INTERNAL_ERROR",
                "error_id": error_id if self.debug else None
            }
        )
    
    async def _log_error(self, exc: Exception, request: Request, error_id: str) -> None:
        """Log error dengan context information"""
        try:
            # Gather request context
            context = {
                "error_id": error_id,
                "method": request.method,
                "url": str(request.url),
                "headers": dict(request.headers),
                "client_ip": self._get_client_ip(request),
                "user_agent": request.headers.get("user-agent", "N/A")
            }
            
            # Log berdasarkan severity
            if isinstance(exc, (HTTPException, BaseCustomException)):
                # Expected errors - log as warning
                logger.warning(
                    f"Expected error [{error_id}]: {exc.__class__.__name__}: {str(exc)}",
                    extra={"context": context}
                )
            else:
                # Unexpected errors - log as error dengan full traceback
                logger.error(
                    f"Unexpected error [{error_id}]: {exc.__class__.__name__}: {str(exc)}",
                    extra={
                        "context": context,
                        "traceback": traceback.format_exc()
                    }
                )
                
        except Exception as log_exc:
            # Jangan biarkan logging error mengganggu error handling
            logger.error(f"Error in error logging: {log_exc}")
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _parse_integrity_error(self, exc: IntegrityError) -> str:
        """Parse integrity error untuk user-friendly message"""
        error_msg = str(exc.orig).lower()
        
        if "unique constraint" in error_msg or "duplicate" in error_msg:
            return "Data sudah ada, tidak dapat menduplikasi"
        elif "foreign key constraint" in error_msg:
            return "Data terkait tidak ditemukan"
        elif "not null constraint" in error_msg:
            return "Field yang diperlukan tidak boleh kosong"
        elif "check constraint" in error_msg:
            return "Data tidak memenuhi kriteria yang ditetapkan"
        else:
            return "Terjadi kesalahan validasi data"
    
    def add_error_handler(self, exc_type: Type[Exception], handler: callable) -> None:
        """
        Tambah custom error handler (Open/Closed Principle)
        
        Args:
            exc_type: Exception type
            handler: Handler function
        """
        self.error_handlers[exc_type] = handler
        logger.info(f"Added custom error handler for {exc_type.__name__}")
