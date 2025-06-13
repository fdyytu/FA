# Domain-Driven Architecture Implementation

## Overview
Proyek ini telah direfactor menggunakan Domain-Driven Design (DDD) untuk meningkatkan maintainability, scalability, dan separation of concerns.

## Struktur Domain

### 1. PPOB Domain (`app/domains/ppob/`)
Domain untuk Payment Point Online Bank yang menangani:
- Inquiry tagihan
- Pembayaran PPOB
- Manajemen produk PPOB
- Transaksi PPOB

**Struktur:**
```
app/domains/ppob/
├── models/
│   └── ppob.py              # Model database PPOB
├── repositories/
│   └── ppob_repository.py   # Repository pattern untuk data access
├── services/
│   └── ppob_service.py      # Business logic PPOB
├── schemas/
│   └── ppob_schemas.py      # Pydantic schemas untuk validation
└── controllers/
    └── ppob_controller.py   # API endpoints PPOB
```

### 2. Wallet Domain (`app/domains/wallet/`)
Domain untuk manajemen wallet dan transaksi keuangan:
- Saldo wallet
- Transfer antar user
- Top up manual dan Midtrans
- Riwayat transaksi

**Struktur:**
```
app/domains/wallet/
├── models/
│   └── wallet.py            # Model database wallet
├── repositories/
│   └── wallet_repository.py # Repository pattern untuk data access
├── services/
│   └── wallet_service.py    # Business logic wallet
├── schemas/
│   └── wallet_schemas.py    # Pydantic schemas untuk validation
└── controllers/
    └── wallet_controller.py # API endpoints wallet
```

## Design Patterns Implemented

### 1. Repository Pattern
- Memisahkan data access logic dari business logic
- Memudahkan testing dengan mock repositories
- Konsisten interface untuk database operations

### 2. Service Layer Pattern
- Mengenkapsulasi business logic
- Koordinasi antara repositories
- Validasi business rules

### 3. Controller Pattern
- Menangani HTTP requests/responses
- Input validation
- Response formatting

### 4. Factory Pattern
- Digunakan untuk provider selection (PPOB)
- Dynamic configuration based on admin settings

### 5. Single Responsibility Principle
- Setiap class memiliki satu tanggung jawab
- Separation of concerns yang jelas

## Base Classes

### 1. BaseRepository
```python
class BaseRepository[T]:
    def __init__(self, db: Session, model: Type[T])
    def create(self, obj: T) -> T
    def get_by_id(self, id: int) -> Optional[T]
    def update(self, id: int, data: dict) -> Optional[T]
    def delete(self, id: int) -> bool
    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]
```

### 2. BaseService
```python
class BaseService[T, R, C, U]:
    def __init__(self, repository: R)
    def create(self, data: C) -> T
    def get_by_id(self, id: int) -> Optional[T]
    def update(self, id: int, data: U) -> Optional[T]
    def delete(self, id: int) -> bool
```

### 3. BaseController
```python
class BaseController[T, S, C, U, R]:
    def __init__(self, service: S, prefix: str, tags: List[str])
    # Standard CRUD endpoints
```

## API Response Format

Semua API menggunakan format response yang konsisten:

```python
class APIResponse[T]:
    success: bool
    message: str
    data: Optional[T]
    error_code: Optional[str]
    timestamp: datetime
```

## Migration Guide

### Dari Legacy ke Domain Architecture

1. **PPOB Endpoints:**
   - Legacy: `/api/v1/ppob/*`
   - New: `/api/v1/ppob/*` (menggunakan domain controller)

2. **Wallet Endpoints:**
   - Legacy: `/api/v1/wallet/*`
   - New: `/api/v1/wallet/*` (menggunakan domain controller)

### Backward Compatibility
- Legacy endpoints masih tersedia
- Gradual migration strategy
- Response format tetap konsisten

## Benefits

### 1. Maintainability
- Code yang lebih terorganisir
- Easier to locate and fix bugs
- Clear separation of concerns

### 2. Scalability
- Easy to add new domains
- Modular architecture
- Independent development

### 3. Testability
- Isolated business logic
- Mockable dependencies
- Unit testing friendly

### 4. Code Reusability
- Base classes untuk common operations
- Shared utilities
- Consistent patterns

## Future Enhancements

### 1. Additional Domains
- User Management Domain
- Notification Domain
- Admin Domain
- Analytics Domain

### 2. Advanced Patterns
- CQRS (Command Query Responsibility Segregation)
- Event Sourcing
- Domain Events

### 3. Infrastructure
- Redis caching layer
- Message queues
- Microservices architecture

## Usage Examples

### PPOB Service Usage
```python
# Dependency injection
repository = PPOBRepository(db)
service = PPOBService(repository)

# Business operations
products = await service.get_products_by_category(PPOBCategory.PULSA)
inquiry = await service.inquiry(inquiry_request)
transaction = await service.create_transaction(user, payment_request)
```

### Wallet Service Usage
```python
# Dependency injection
repository = WalletRepository(db)
service = WalletService(repository)

# Business operations
balance = service.get_user_balance(user_id)
transfer = service.transfer_money(sender_id, transfer_request)
topup = service.create_manual_topup_request(user_id, topup_request)
```

## Testing Strategy

### Unit Tests
- Test business logic in services
- Mock repositories for isolation
- Test edge cases and error handling

### Integration Tests
- Test repository with real database
- Test API endpoints
- Test external service integrations

### Example Test Structure
```python
class TestPPOBService:
    def test_inquiry_success(self, mock_repository):
        # Test successful inquiry
        pass
    
    def test_inquiry_invalid_customer(self, mock_repository):
        # Test error handling
        pass
```

## Conclusion

Domain-driven architecture memberikan foundation yang solid untuk:
- Scalable application development
- Maintainable codebase
- Clear business logic separation
- Consistent API design
- Easy testing and debugging

Implementasi ini mengikuti best practices dan design patterns yang telah terbukti dalam enterprise applications.
