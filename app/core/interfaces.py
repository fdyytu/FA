"""
Abstract Base Classes dan Interfaces untuk implementasi SOLID principles
Interface Segregation Principle - pisahkan interface berdasarkan tanggung jawab
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Generic, TypeVar
from pydantic import BaseModel

# Type variables untuk generic interfaces
T = TypeVar('T')
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)
ResponseSchemaType = TypeVar('ResponseSchemaType', bound=BaseModel)


class IRepository(ABC, Generic[T]):
    """
    Interface untuk Repository Pattern
    Single Responsibility: Hanya menangani data access
    """
    
    @abstractmethod
    async def create(self, obj_in: CreateSchemaType) -> T:
        """Buat record baru"""
        pass
    
    @abstractmethod
    async def get(self, id: Any) -> Optional[T]:
        """Ambil record berdasarkan ID"""
        pass
    
    @abstractmethod
    async def get_multi(
        self, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[T]:
        """Ambil multiple records dengan pagination dan filter"""
        pass
    
    @abstractmethod
    async def update(self, db_obj: T, obj_in: UpdateSchemaType) -> T:
        """Update record yang sudah ada"""
        pass
    
    @abstractmethod
    async def delete(self, id: Any) -> bool:
        """Hapus record berdasarkan ID"""
        pass
    
    @abstractmethod
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Hitung jumlah records dengan filter"""
        pass


class IService(ABC, Generic[T, CreateSchemaType, UpdateSchemaType]):
    """
    Interface untuk Service Layer
    Single Responsibility: Business logic
    """
    
    @abstractmethod
    async def create(self, obj_in: CreateSchemaType) -> T:
        """Buat entitas baru dengan business logic"""
        pass
    
    @abstractmethod
    async def get(self, id: Any) -> Optional[T]:
        """Ambil entitas dengan business logic"""
        pass
    
    @abstractmethod
    async def update(self, id: Any, obj_in: UpdateSchemaType) -> Optional[T]:
        """Update entitas dengan business logic"""
        pass
    
    @abstractmethod
    async def delete(self, id: Any) -> bool:
        """Hapus entitas dengan business logic"""
        pass


class IAuthService(ABC):
    """Interface untuk Authentication Service"""
    
    @abstractmethod
    async def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Autentikasi user"""
        pass
    
    @abstractmethod
    async def create_access_token(self, data: Dict[str, Any]) -> str:
        """Buat access token"""
        pass
    
    @abstractmethod
    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verifikasi token"""
        pass
    
    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> Optional[Dict[str, str]]:
        """Refresh access token"""
        pass


class INotificationService(ABC):
    """Interface untuk Notification Service"""
    
    @abstractmethod
    async def send_email(self, to: str, subject: str, body: str) -> bool:
        """Kirim email notification"""
        pass
    
    @abstractmethod
    async def send_sms(self, phone: str, message: str) -> bool:
        """Kirim SMS notification"""
        pass
    
    @abstractmethod
    async def send_push_notification(self, user_id: str, title: str, body: str) -> bool:
        """Kirim push notification"""
        pass


class IPPOBProvider(ABC):
    """Interface untuk PPOB Provider"""
    
    @abstractmethod
    async def get_products(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Ambil daftar produk PPOB"""
        pass
    
    @abstractmethod
    async def check_balance(self) -> Dict[str, Any]:
        """Cek saldo provider"""
        pass
    
    @abstractmethod
    async def create_transaction(self, product_code: str, customer_id: str, amount: float) -> Dict[str, Any]:
        """Buat transaksi PPOB"""
        pass
    
    @abstractmethod
    async def check_transaction_status(self, transaction_id: str) -> Dict[str, Any]:
        """Cek status transaksi"""
        pass


class IPaymentGateway(ABC):
    """Interface untuk Payment Gateway"""
    
    @abstractmethod
    async def create_payment(self, amount: float, order_id: str, customer_details: Dict[str, Any]) -> Dict[str, Any]:
        """Buat pembayaran"""
        pass
    
    @abstractmethod
    async def check_payment_status(self, order_id: str) -> Dict[str, Any]:
        """Cek status pembayaran"""
        pass
    
    @abstractmethod
    async def cancel_payment(self, order_id: str) -> Dict[str, Any]:
        """Batalkan pembayaran"""
        pass


class ICacheService(ABC):
    """Interface untuk Cache Service"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Ambil data dari cache"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """Simpan data ke cache"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Hapus data dari cache"""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Cek apakah key ada di cache"""
        pass


class IFileService(ABC):
    """Interface untuk File Service"""
    
    @abstractmethod
    async def upload_file(self, file_data: bytes, filename: str, content_type: str) -> Dict[str, Any]:
        """Upload file"""
        pass
    
    @abstractmethod
    async def delete_file(self, file_path: str) -> bool:
        """Hapus file"""
        pass
    
    @abstractmethod
    async def get_file_url(self, file_path: str) -> str:
        """Dapatkan URL file"""
        pass


class IEventBus(ABC):
    """Interface untuk Event Bus"""
    
    @abstractmethod
    async def publish(self, event_type: str, data: Dict[str, Any]) -> bool:
        """Publish event"""
        pass
    
    @abstractmethod
    async def subscribe(self, event_type: str, handler: callable) -> bool:
        """Subscribe ke event"""
        pass


class IValidator(ABC):
    """Interface untuk Validator"""
    
    @abstractmethod
    def validate(self, data: Any) -> bool:
        """Validasi data"""
        pass
    
    @abstractmethod
    def get_errors(self) -> List[str]:
        """Dapatkan error messages"""
        pass


class ILogger(ABC):
    """Interface untuk Logger"""
    
    @abstractmethod
    def info(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log info message"""
        pass
    
    @abstractmethod
    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log warning message"""
        pass
    
    @abstractmethod
    def error(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log error message"""
        pass
    
    @abstractmethod
    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log debug message"""
        pass


class IHealthChecker(ABC):
    """Interface untuk Health Checker"""
    
    @abstractmethod
    async def check_database(self) -> Dict[str, Any]:
        """Cek kesehatan database"""
        pass
    
    @abstractmethod
    async def check_external_services(self) -> Dict[str, Any]:
        """Cek kesehatan external services"""
        pass
    
    @abstractmethod
    async def get_system_info(self) -> Dict[str, Any]:
        """Dapatkan informasi sistem"""
        pass
