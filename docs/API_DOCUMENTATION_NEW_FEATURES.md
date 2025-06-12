# API Documentation - New Features

## Overview
Dokumentasi ini menjelaskan fitur-fitur baru yang telah ditambahkan ke sistem FA:

1. **User Profile Management** - Manajemen profil user lengkap
2. **Transaction Management** - Sistem transaksi dan mutasi harian
3. **Multi-Channel Notifications** - Notifikasi via Email, WhatsApp, Discord
4. **Webhook Integration** - Integrasi webhook untuk update status transaksi
5. **Admin Management** - Sistem admin dengan role-based access

## Authentication
Semua endpoint memerlukan authentication kecuali yang disebutkan khusus. Gunakan Bearer token di header:
```
Authorization: Bearer <your_jwt_token>
```

---

## 1. User Profile Management

### Create User Profile
**POST** `/api/v1/users/profile`

Membuat profil user baru.

**Request Body:**
```json
{
  "avatar_url": "https://example.com/avatar.jpg",
  "birth_date": "1990-01-01T00:00:00Z",
  "address": "Jl. Contoh No. 123",
  "city": "Jakarta",
  "province": "DKI Jakarta",
  "postal_code": "12345",
  "identity_number": "1234567890123456",
  "bank_account": "1234567890",
  "bank_name": "Bank ABC"
}
```

### Get User Profile
**GET** `/api/v1/users/profile`

### Update User Profile
**PUT** `/api/v1/users/profile`

### Get User Detail
**GET** `/api/v1/users/detail`

### Admin Endpoints
- **GET** `/api/v1/users/admin/users` - Get users list (Admin Only)
- **POST** `/api/v1/users/admin/users/{user_id}/toggle-status` - Toggle user status
- **GET** `/api/v1/users/admin/statistics` - Get user statistics

---

## 2. Transaction Management

### Create Transaction
**POST** `/api/v1/transactions/`

### Update Transaction (Admin Only)
**PUT** `/api/v1/transactions/{transaction_id}`

### Get Transaction History
**GET** `/api/v1/transactions/history`

### Get Transaction Summary
**GET** `/api/v1/transactions/summary`

### Daily Mutation Endpoints (Admin Only)
- **POST** `/api/v1/transactions/daily-mutation/generate` - Generate daily mutation
- **GET** `/api/v1/transactions/daily-mutation` - Get daily mutations
- **GET** `/api/v1/transactions/daily-mutation/summary` - Get mutation summary

---

## 3. Multi-Channel Notifications

### User Notifications
- **GET** `/api/v1/notifications/` - Get user notifications
- **POST** `/api/v1/notifications/{notification_id}/read` - Mark as read

### Admin Notifications
- **POST** `/api/v1/notifications/admin/send` - Send admin notification
- **POST** `/api/v1/notifications/admin/settings` - Create notification setting

### Test Notifications (Admin Only)
- **POST** `/api/v1/notifications/test/email` - Test email
- **POST** `/api/v1/notifications/test/whatsapp` - Test WhatsApp
- **POST** `/api/v1/notifications/test/discord` - Test Discord

---

## 4. Webhook Integration

### Digiflazz Webhook
**POST** `/api/v1/notifications/webhook/digiflazz`

### Webhook Logs
**GET** `/api/v1/notifications/webhook/logs` - Get webhook logs (Admin Only)

---

## 5. Environment Variables

```bash
# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# WhatsApp Configuration
WHATSAPP_API_URL=https://graph.facebook.com/v17.0/YOUR_PHONE_ID/messages
WHATSAPP_API_TOKEN=your-whatsapp-token

# Firebase Cloud Messaging
FCM_SERVER_KEY=your-fcm-server-key

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

---

## 6. Background Tasks

### Available Tasks
1. `generate_daily_mutation_task` - Generate mutasi harian (otomatis jam 1 pagi)
2. `send_daily_report_task` - Kirim laporan harian (otomatis jam 8 pagi)
3. `test_notification_task` - Test notifikasi

---

## 7. Database Migration

Jalankan migrasi database:
```bash
alembic upgrade head
```

### New Tables Added
1. `admins` - Data admin sistem
2. `user_profiles` - Profil lengkap user
3. `transactions` - Data transaksi
4. `daily_mutations` - Mutasi harian
5. `notifications` - Notifikasi user
6. `admin_notification_settings` - Pengaturan notifikasi admin
7. `webhook_logs` - Log webhook requests
