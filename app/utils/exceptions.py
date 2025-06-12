from fastapi import HTTPException, status

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

class NotFoundError(HTTPException):
    """Exception untuk resource tidak ditemukan"""
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class ConflictError(HTTPException):
    """Exception untuk konflik data"""
    def __init__(self, detail: str = "Data conflict"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)

class PPOBError(HTTPException):
    """Exception untuk error PPOB"""
    def __init__(self, detail: str = "PPOB service error"):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)

class InsufficientBalanceError(HTTPException):
    """Exception untuk saldo tidak cukup"""
    def __init__(self, detail: str = "Insufficient balance"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

class TransactionError(HTTPException):
    """Exception untuk error transaksi"""
    def __init__(self, detail: str = "Transaction error"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
