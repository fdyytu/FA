# PPOB API - SOLID Principles Implementation

Payment Point Online Bank (PPOB) API yang dibangun dengan implementasi SOLID principles menggunakan FastAPI.

## 🏗️ Arsitektur & SOLID Principles

### Single Responsibility Principle (SRP)
- **Middleware**: Setiap middleware memiliki tanggung jawab spesifik
  - `SecurityMiddleware`: Menangani keamanan HTTP requests
  - `RateLimiterMiddleware`: Menangani pembatasan request rate
  - `ErrorHandlerMiddleware`: Menangani error handling secara terpusat
- **Services**: Setiap service menangani satu domain bisnis
- **Repositories**: Hanya menangani data access layer

### Open/Closed Principle (OCP)
- **Error Handler**: Mudah menambah handler untuk exception types baru
- **Middleware**: Dapat menambah middleware baru tanpa mengubah existing code
- **Services**: Interface-based design memungkinkan extensibility

### Liskov Substitution Principle (LSP)
- **Repository Pattern**: Implementasi repository dapat diganti tanpa mengubah business logic
- **Service Interfaces**: Concrete services dapat diganti dengan implementasi lain

### Interface Segregation Principle (ISP)
- **Interfaces**: Terpisah berdasarkan concern (IRepository, IService, IAuthService, dll)
- **Clients**: Hanya bergantung pada interface yang mereka butuhkan

### Dependency Inversion Principle (DIP)
- **Dependency Injection Container**: Mengelola dependencies secara terpusat
- **Abstraction**: High-level modules bergantung pada abstraksi, bukan implementasi konkret

## 🚀 Fitur Utama

### Core Features
- ✅ **Authentication & Authorization** dengan JWT
- ✅ **Rate Limiting** dengan sliding window algorithm
- ✅ **Security Middleware** (CSRF, XSS protection, Security headers)
- ✅ **Global Error Handling** dengan custom exceptions
- ✅ **Dependency Injection Container**
- ✅ **Repository Pattern** untuk data access
- ✅ **Comprehensive Logging**

### Business Features
- 🔐 **User Management** (Registration, Login, Profile)
- 💰 **Wallet Management** (Balance, Top-up, History)
- 📱 **PPOB Services** (Pulsa, Data, PLN, PDAM, dll)
- 💳 **Payment Gateway Integration** (Midtrans)
- 📊 **Transaction Management**
- 👨‍💼 **Admin Panel**

## 📁 Struktur Proyek

```
workspace/
├── app/
│   ├── api/v1/                 # API endpoints
│   ├── core/                   # Core components
│   │   ├── config.py          # Configuration
│   │   ├── database.py        # Database setup
│   │   ├── interfaces.py      # Interface definitions
│   │   ├── container.py       # DI Container
│   │   └── constants.py       # Constants
│   ├── middleware/             # Custom middleware
│   │   ├── security.py        # Security middleware
│   │   ├── rate_limiter.py    # Rate limiting
│   │   └── error_handler.py   # Error handling
│   ├── models/                 # SQLAlchemy models
│   ├── repositories/           # Repository pattern
│   │   └── base_repository.py # Base repository
│   ├── services/               # Business logic
│   ├── utils/                  # Utilities
│   │   ├── decorators.py      # Reusable decorators
│   │   └── exceptions.py      # Custom exceptions
│   └── schemas/                # Pydantic schemas
├── main.py                     # Application entry point
├── requirements.txt            # Dependencies
└── README.md                   # Documentation
```

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.8+
- PostgreSQL
- Redis (optional, untuk production caching)

### Installation

1. **Clone repository**
```bash
git clone <repository-url>
cd workspace
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# atau
venv\Scripts\activate     # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment setup**
```bash
cp .env.example .env
# Edit .env dengan konfigurasi yang sesuai
```

5. **Database setup**
```bash
# Buat database PostgreSQL
createdb ppob_api

# Run migrations (jika menggunakan Alembic)
alembic upgrade head
```

6. **Run application**
```bash
# Development
python main.py

# Production
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 🔧 Configuration

### Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:password@localhost/ppob_api

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# External Services
DIGIFLAZZ_USERNAME=your-username
DIGIFLAZZ_API_KEY=your-api-key
MIDTRANS_SERVER_KEY=your-server-key
MIDTRANS_CLIENT_KEY=your-client-key

# Application
DEBUG=True
ALLOWED_HOSTS=["localhost", "127.0.0.1"]
```

## 📚 API Documentation

### Authentication
```bash
# Register
POST /api/v1/auth/register
{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "John Doe",
  "phone": "08123456789"
}

# Login
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "password123"
}
```

### Wallet Management
```bash
# Get balance
GET /api/v1/wallet/balance
Authorization: Bearer <token>

# Top up
POST /api/v1/wallet/topup
Authorization: Bearer <token>
{
  "amount": 100000,
  "payment_method": "bank_transfer"
}
```

### PPOB Services
```bash
# Get products
GET /api/v1/ppob/products?category=pulsa

# Purchase
POST /api/v1/ppob/purchase
Authorization: Bearer <token>
{
  "product_code": "TSEL5",
  "customer_number": "08123456789",
  "amount": 5000
}
```

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test
pytest tests/test_auth.py
```

## 🔒 Security Features

### Rate Limiting
- **Authentication endpoints**: 5 requests/minute
- **PPOB endpoints**: 30 requests/minute
- **General API**: 60 requests/minute
- **Admin endpoints**: 100 requests/minute

### Security Headers
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security`
- `Content-Security-Policy`

### Input Validation
- Request size limits
- SQL injection protection
- XSS protection
- CSRF protection

## 📊 Monitoring & Logging

### Health Checks
```bash
# Basic health check
GET /health

# Detailed health check
GET /health/detailed
```

### Logging
- Structured logging dengan context
- Error tracking dengan unique IDs
- Audit logging untuk sensitive operations
- Performance monitoring

## 🚀 Deployment

### Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/ppob_api
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: ppob_api
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

## 🤝 Contributing

1. Fork repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Code Style
- Follow PEP 8
- Use Black untuk formatting
- Use isort untuk import sorting
- Add type hints
- Write docstrings

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- FastAPI framework
- SQLAlchemy ORM
- Pydantic validation
- SOLID principles community
- Clean Architecture patterns

## 📞 Support

Untuk pertanyaan atau dukungan:
- Email: support@ppobapi.com
- Documentation: [docs.ppobapi.com](https://docs.ppobapi.com)
- Issues: [GitHub Issues](https://github.com/your-repo/issues)
