# User Management API Documentation

## Overview
API ini menyediakan endpoint lengkap untuk manajemen user dengan arsitektur yang mengikuti prinsip SOLID dan Clean Architecture.

## Architecture

### Struktur Folder
```
app/
├── api/v1/endpoints/users/
│   ├── __init__.py          # Router configuration
│   ├── profile.py           # User profile endpoints
│   ├── settings.py          # User settings endpoints
│   └── admin.py             # Admin user management endpoints
├── domains/user/services/
│   ├── user_profile_service.py    # Profile management service
│   ├── user_settings_service.py   # Settings management service
│   ├── user_security_service.py   # Security management service
│   └── user_management_service.py # Admin management service
├── schemas/user_profile.py         # Pydantic schemas
├── middleware/security.py          # Security middleware
└── shared/base_classes/base_service.py # Base service class
```

### Design Principles Applied

1. **Single Responsibility Principle (SRP)**
   - Setiap service memiliki tanggung jawab yang spesifik
   - UserProfileService: Mengelola profil user
   - UserSettingsService: Mengelola pengaturan user
   - UserSecurityService: Mengelola keamanan user
   - UserManagementService: Mengelola user untuk admin

2. **Open/Closed Principle (OCP)**
   - BaseService dapat diperluas tanpa modifikasi
   - Service baru dapat inherit dari BaseService

3. **Liskov Substitution Principle (LSP)**
   - Semua service dapat menggantikan BaseService
   - Interface yang konsisten

4. **Interface Segregation Principle (ISP)**
   - Endpoint dipisah berdasarkan fungsi
   - User biasa dan admin memiliki endpoint terpisah

5. **Dependency Inversion Principle (DIP)**
   - Service bergantung pada abstraksi (BaseService)
   - Dependency injection melalui FastAPI

## API Endpoints

### User Profile Endpoints (untuk user biasa)

#### 1. Get User Profile
```
GET /api/v1/users/profile
```
**Description:** Mendapatkan profil user yang sedang login

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "full_name": "John Doe",
    "phone_number": "+6281234567890",
    "balance": 100000.0,
    "is_active": true,
    "created_at": "2024-01-01T00:00:00",
    "profile": {
      "id": 1,
      "user_id": 1,
      "avatar_url": "/static/uploads/avatars/1_avatar.jpg",
      "birth_date": "1990-01-01T00:00:00",
      "address": "Jl. Sudirman No. 1",
      "city": "Jakarta",
      "province": "DKI Jakarta",
      "postal_code": "12345",
      "identity_number": "1234567890123456",
      "bank_account": "1234567890",
      "bank_name": "BCA",
      "identity_verified": "verified",
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00"
    }
  },
  "message": "Profil berhasil diambil"
}
```

#### 2. Create User Profile
```
POST /api/v1/users/profile
```
**Description:** Membuat profil user baru

**Request Body:**
```json
{
  "birth_date": "1990-01-01T00:00:00",
  "address": "Jl. Sudirman No. 1",
  "city": "Jakarta",
  "province": "DKI Jakarta",
  "postal_code": "12345",
  "identity_number": "1234567890123456",
  "bank_account": "1234567890",
  "bank_name": "BCA"
}
```

#### 3. Update User Profile
```
PUT /api/v1/users/profile
```
**Description:** Update profil user

#### 4. Upload Avatar
```
POST /api/v1/users/profile/avatar
```
**Description:** Upload avatar user

**Request:** Multipart form data dengan file image

#### 5. Delete Avatar
```
DELETE /api/v1/users/profile/avatar
```
**Description:** Hapus avatar user

### User Settings Endpoints

#### 1. Get User Settings
```
GET /api/v1/users/settings
```
**Description:** Mendapatkan pengaturan user

**Response:**
```json
{
  "success": true,
  "data": {
    "notifications": {
      "email_notifications": true,
      "push_notifications": true,
      "transaction_alerts": true,
      "marketing_emails": false
    },
    "privacy": {
      "profile_visibility": "public",
      "show_balance": false,
      "show_transaction_history": false
    },
    "security": {
      "two_factor_enabled": false,
      "login_alerts": true,
      "session_timeout": 30
    },
    "display": {
      "language": "id",
      "timezone": "Asia/Jakarta",
      "currency": "IDR",
      "theme": "light"
    }
  },
  "message": "Pengaturan berhasil diambil"
}
```

#### 2. Update User Settings
```
PUT /api/v1/users/settings
```
**Description:** Update pengaturan user

#### 3. Change Password
```
POST /api/v1/users/change-password
```
**Description:** Ganti password user

**Request Body:**
```json
{
  "current_password": "old_password",
  "new_password": "new_password",
  "confirm_password": "new_password"
}
```

#### 4. Get Security Settings
```
GET /api/v1/users/security
```
**Description:** Mendapatkan pengaturan keamanan

#### 5. Enable 2FA
```
POST /api/v1/users/enable-2fa
```
**Description:** Aktifkan 2FA

**Response:**
```json
{
  "success": true,
  "data": {
    "qr_code_url": "data:image/png;base64,..."
  },
  "message": "2FA berhasil diaktifkan. Scan QR code dengan aplikasi authenticator"
}
```

#### 6. Disable 2FA
```
POST /api/v1/users/disable-2fa
```
**Description:** Nonaktifkan 2FA

#### 7. Get Activity Logs
```
GET /api/v1/users/activity-logs?page=1&limit=20
```
**Description:** Mendapatkan log aktivitas user

#### 8. Get User Preferences
```
GET /api/v1/users/preferences
```
**Description:** Mendapatkan preferensi user

#### 9. Update User Preferences
```
PUT /api/v1/users/preferences
```
**Description:** Update preferensi user

### Admin User Management Endpoints

#### 1. Get Users List
```
GET /api/v1/users/admin/users?page=1&limit=10&search=john&status=active
```
**Description:** Mendapatkan daftar user (untuk admin)

**Query Parameters:**
- `page`: Halaman (default: 1)
- `limit`: Jumlah per halaman (default: 10, max: 100)
- `search`: Pencarian berdasarkan username, email, nama, atau nomor telepon
- `status`: Filter status (active, inactive, all)

**Response:**
```json
{
  "success": true,
  "data": {
    "users": [
      {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "full_name": "John Doe",
        "phone_number": "+6281234567890",
        "balance": 100000.0,
        "is_active": true,
        "created_at": "2024-01-01T00:00:00",
        "last_transaction_date": "2024-01-15T10:30:00",
        "total_transactions": 25
      }
    ],
    "page": 1,
    "limit": 10,
    "total": 100,
    "total_pages": 10
  },
  "message": "Daftar user berhasil diambil"
}
```

#### 2. Get User Detail
```
GET /api/v1/users/admin/users/{user_id}
```
**Description:** Mendapatkan detail user tertentu (untuk admin)

#### 3. Toggle User Status
```
POST /api/v1/users/admin/users/{user_id}/toggle-status
```
**Description:** Toggle status aktif/nonaktif user

#### 4. Verify User Identity
```
POST /api/v1/users/admin/users/{user_id}/verify-identity
```
**Description:** Verifikasi identitas user

#### 5. Reset User Password
```
POST /api/v1/users/admin/users/{user_id}/reset-password
```
**Description:** Reset password user

**Response:**
```json
{
  "success": true,
  "data": {
    "temporary_password": "TempPass123!"
  },
  "message": "Password user berhasil direset. Password sementara telah digenerate."
}
```

#### 6. Delete User
```
DELETE /api/v1/users/admin/users/{user_id}
```
**Description:** Hapus user (soft delete)

#### 7. Get User Statistics
```
GET /api/v1/users/admin/statistics
```
**Description:** Mendapatkan statistik user untuk dashboard admin

**Response:**
```json
{
  "success": true,
  "data": {
    "total_users": 1000,
    "active_users": 850,
    "inactive_users": 150,
    "top_balance_users": [
      {
        "id": 1,
        "username": "john_doe",
        "full_name": "John Doe",
        "balance": 1000000.0
      }
    ],
    "top_transaction_users": [
      {
        "id": 2,
        "username": "jane_doe",
        "full_name": "Jane Doe",
        "transaction_count": 100
      }
    ],
    "monthly_registrations": [
      {
        "month": "2024-01",
        "count": 50
      }
    ]
  },
  "message": "Statistik user berhasil diambil"
}
```

#### 8. Export Users Data
```
GET /api/v1/users/admin/export?format=csv
```
**Description:** Export data user ke CSV atau Excel

**Query Parameters:**
- `format`: Format export (csv, excel)

## Security Features

### 1. Authentication & Authorization
- JWT token authentication
- Role-based access control (user vs admin)
- Active user validation
- Resource ownership validation

### 2. Rate Limiting
- API rate limiting (1000 requests/hour)
- Auth rate limiting (10 attempts/5 minutes)
- Per-user rate limiting

### 3. Security Headers
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block
- Strict-Transport-Security
- Content-Security-Policy

### 4. Input Validation
- Pydantic schema validation
- Password strength validation
- File type validation for uploads

### 5. Audit Logging
- User activity logging
- Admin action logging
- Error logging

## Error Handling

### Standard Error Response
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Data tidak valid",
    "details": {
      "field": "error_message"
    }
  }
}
```

### HTTP Status Codes
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `422`: Validation Error
- `429`: Too Many Requests
- `500`: Internal Server Error

## Usage Examples

### 1. Get User Profile
```bash
curl -X GET "http://localhost:8000/api/v1/users/profile"   -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 2. Update User Settings
```bash
curl -X PUT "http://localhost:8000/api/v1/users/settings"   -H "Authorization: Bearer YOUR_JWT_TOKEN"   -H "Content-Type: application/json"   -d '{
    "notifications": {
      "email_notifications": false
    }
  }'
```

### 3. Admin: Get Users List
```bash
curl -X GET "http://localhost:8000/api/v1/users/admin/users?page=1&limit=10"   -H "Authorization: Bearer ADMIN_JWT_TOKEN"
```

## Testing

### Unit Tests
- Service layer testing
- Schema validation testing
- Business logic testing

### Integration Tests
- API endpoint testing
- Database integration testing
- Authentication testing

### Performance Tests
- Load testing
- Rate limiting testing
- Database query optimization

## Deployment Considerations

### Environment Variables
```env
DATABASE_URL=postgresql://user:pass@localhost/db
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
UPLOAD_DIR=/app/static/uploads
EXPORT_DIR=/app/static/exports
```

### Database Migrations
- Alembic migrations for schema changes
- Data migration scripts
- Backup and restore procedures

### Monitoring
- Application performance monitoring
- Error tracking
- User activity monitoring
- Database performance monitoring

## Future Enhancements

1. **Real-time Features**
   - WebSocket for real-time notifications
   - Live user activity tracking

2. **Advanced Security**
   - OAuth2 integration
   - SAML authentication
   - Advanced fraud detection

3. **Analytics**
   - User behavior analytics
   - Transaction pattern analysis
   - Predictive analytics

4. **Mobile Support**
   - Mobile-optimized endpoints
   - Push notification service
   - Offline capability

5. **Scalability**
   - Microservices architecture
   - Event-driven architecture
   - Caching layer optimization
