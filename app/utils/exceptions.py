from fastapi import HTTPException, status
from typing import Any, Dict, List, Optional


class BaseCustomException(Exception):
    """
    Base custom exception untuk aplikasi
    Menggunakan composition pattern untuk flexibility
    """
    
    def __init__(
        self, 
        message: str, 
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationException(BaseCustomException):
    """Exception untuk validation errors"""
    
    def __init__(self, message: str = "Validation error", errors: Optional[List[str]] = None):
        super().__init__(
            message=message,
            status_code=400,
            error_code="VALIDATION_ERROR"
        )
        self.errors = errors or []


class NotFoundError(BaseCustomException):
    """Exception untuk resource not found"""
    
    def __init__(self, message: str = "Resource tidak ditemukan", resource_type: str = ""):
        super().__init__(
            message=message,
            status_code=404,
            error_code="NOT_FOUND",
            details={"resource_type": resource_type} if resource_type else {}
        )


class UnauthorizedError(BaseCustomException):
    """Exception untuk unauthorized access"""
    
    def __init__(self, message: str = "Tidak memiliki akses"):
        super().__init__(
            message=message,
            status_code=401,
            error_code="UNAUTHORIZED"
        )


class ForbiddenError(BaseCustomException):
    """Exception untuk forbidden access"""
    
    def __init__(self, message: str = "Akses ditolak"):
        super().__init__(
            message=message,
            status_code=403,
            error_code="FORBIDDEN"
        )


class ConflictError(BaseCustomException):
    """Exception untuk conflict situations"""
    
    def __init__(self, message: str = "Konflik data", conflict_field: str = ""):
        super().__init__(
            message=message,
            status_code=409,
            error_code="CONFLICT",
            details={"conflict_field": conflict_field} if conflict_field else {}
        )


class InternalServerError(BaseCustomException):
    """Exception untuk internal server errors"""
    
    def __init__(self, message: str = "Terjadi kesalahan internal"):
        super().__init__(
            message=message,
            status_code=500,
            error_code="INTERNAL_ERROR"
        )


class BusinessLogicError(BaseCustomException):
    """Exception untuk business logic violations"""
    
    def __init__(self, message: str, rule: str = ""):
        super().__init__(
            message=message,
            status_code=400,
            error_code="BUSINESS_LOGIC_ERROR",
            details={"violated_rule": rule} if rule else {}
        )


class ExternalServiceError(BaseCustomException):
    """Exception untuk external service errors"""
    
    def __init__(self, message: str, service_name: str = "", status_code: int = 502):
        super().__init__(
            message=message,
            status_code=status_code,
            error_code="EXTERNAL_SERVICE_ERROR",
            details={"service_name": service_name} if service_name else {}
        )


class RateLimitExceededError(BaseCustomException):
    """Exception untuk rate limit exceeded"""
    
    def __init__(self, message: str = "Terlalu banyak permintaan", retry_after: int = 60):
        super().__init__(
            message=message,
            status_code=429,
            error_code="RATE_LIMIT_EXCEEDED",
            details={"retry_after": retry_after}
        )


class PaymentError(BaseCustomException):
    """Exception untuk payment-related errors"""
    
    def __init__(self, message: str, payment_id: str = "", error_type: str = ""):
        super().__init__(
            message=message,
            status_code=400,
            error_code="PAYMENT_ERROR",
            details={
                "payment_id": payment_id,
                "error_type": error_type
            }
        )


# Legacy HTTP exceptions untuk backward compatibility
class AuthenticationError(HTTPException):
    """Exception untuk error autentikasi"""
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class AuthorizationError(HTTPException):
    """Exception untuk error autorisasi"""
    def __init__(self, detail: str = "Not authorized"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class ValidationError(HTTPException):
    """Exception untuk error validasi"""
    def __init__(self, detail: str = "Validation error"):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)


class PPOBError(BaseCustomException):
    """Exception untuk PPOB-related errors"""
    
    def __init__(self, message: str, provider: str = "", product_code: str = ""):
        super().__init__(
            message=message,
            status_code=400,
            error_code="PPOB_ERROR",
            details={
                "provider": provider,
                "product_code": product_code
            }
        )


class InsufficientBalanceError(BaseCustomException):
    """Exception untuk saldo tidak cukup"""
    
    def __init__(self, message: str = "Saldo tidak mencukupi", current_balance: float = 0, required_amount: float = 0):
        super().__init__(
            message=message,
            status_code=400,
            error_code="INSUFFICIENT_BALANCE",
            details={
                "current_balance": current_balance,
                "required_amount": required_amount
            }
        )


class TransactionError(BaseCustomException):
    """Exception untuk error transaksi"""
    
    def __init__(self, message: str, transaction_id: str = "", error_type: str = ""):
        super().__init__(
            message=message,
            status_code=400,
            error_code="TRANSACTION_ERROR",
            details={
                "transaction_id": transaction_id,
                "error_type": error_type
            }
        )


# Utility functions untuk exception handling
def create_validation_error(field: str, message: str) -> ValidationException:
    """Helper untuk create validation error"""
    return ValidationException(
        message=f"Validation error pada field {field}",
        errors=[f"{field}: {message}"]
    )


def create_not_found_error(resource_type: str, identifier: Any) -> NotFoundError:
    """Helper untuk create not found error"""
    return NotFoundError(
        message=f"{resource_type} dengan ID {identifier} tidak ditemukan",
        resource_type=resource_type
    )


def create_conflict_error(field: str, value: Any) -> ConflictError:
    """Helper untuk create conflict error"""
    return ConflictError(
        message=f"Data dengan {field} '{value}' sudah ada",
        conflict_field=field
    )
