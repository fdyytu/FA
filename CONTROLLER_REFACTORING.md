# Controller Refactoring Documentation

## Overview
Proyek ini telah direfactor untuk memecah controller monolitik menjadi controller yang lebih kecil dan terfokus berdasarkan **Single Responsibility Principle (SRP)**. Setiap controller sekarang memiliki tanggung jawab yang spesifik dan terpisah.

## Admin Controllers

### 1. AuthController (`auth_controller.py`)
**Tanggung Jawab**: Autentikasi admin
- `POST /login` - Login admin
- `POST /logout` - Logout admin

### 2. AdminManagementController (`admin_management_controller.py`)
**Tanggung Jawab**: Manajemen admin
- `GET /` - Ambil daftar admin
- `POST /` - Buat admin baru
- `GET /{admin_id}` - Ambil detail admin
- `PUT /{admin_id}` - Update admin
- `DELETE /{admin_id}` - Hapus admin
- `GET /audit-logs/` - Ambil audit logs

### 3. ConfigurationController (`configuration_controller.py`)
**Tanggung Jawab**: Konfigurasi sistem
- `GET /system` - Ambil semua konfigurasi sistem
- `POST /system` - Buat konfigurasi baru
- `PUT /system/{key}` - Update konfigurasi
- `DELETE /system/{key}` - Hapus konfigurasi
- `GET /margins` - Ambil konfigurasi margin
- `POST /margins` - Buat konfigurasi margin
- `PUT /margins/{margin_id}` - Update margin
- `DELETE /margins/{margin_id}` - Hapus margin
- `GET /discord` - Ambil konfigurasi Discord
- `POST /discord` - Buat konfigurasi Discord
- `PUT /discord/{config_id}` - Update Discord config
- `DELETE /discord/{config_id}` - Hapus Discord config

### 4. UserManagementController (`user_management_controller.py`)
**Tanggung Jawab**: Manajemen user
- `GET /` - Ambil daftar user
- `GET /stats` - Ambil statistik user
- `GET /{user_id}` - Ambil detail user
- `PUT /{user_id}` - Update user
- `DELETE /{user_id}` - Hapus user
- `POST /{user_id}/activate` - Aktifkan user
- `POST /{user_id}/deactivate` - Nonaktifkan user
- `POST /{user_id}/reset-password` - Reset password user

### 5. ProductManagementController (`product_management_controller.py`)
**Tanggung Jawab**: Manajemen produk
- `GET /` - Ambil daftar produk
- `GET /categories` - Ambil kategori produk
- `GET /stats` - Ambil statistik produk
- `POST /` - Buat produk baru
- `GET /{product_id}` - Ambil detail produk
- `PUT /{product_id}` - Update produk
- `DELETE /{product_id}` - Hapus produk
- `POST /{product_id}/activate` - Aktifkan produk
- `POST /{product_id}/deactivate` - Nonaktifkan produk
- `POST /{product_id}/update-stock` - Update stok produk

### 6. DashboardController (`dashboard_controller.py`)
**Tanggung Jawab**: Dashboard dan statistik
- `GET /` - Ambil data dashboard
- `GET /stats/overview` - Ambil statistik overview
- `GET /stats/users` - Ambil statistik user
- `GET /stats/transactions` - Ambil statistik transaksi
- `GET /stats/products` - Ambil statistik produk
- `GET /stats/revenue` - Ambil statistik revenue
- `GET /recent-activities` - Ambil aktivitas terbaru
- `GET /system-health` - Ambil status kesehatan sistem
- `GET /alerts` - Ambil alert sistem

### 7. TransactionController (`transaction_controller.py`)
**Tanggung Jawab**: Manajemen transaksi
- `GET /recent` - Ambil transaksi terbaru
- `GET /` - Ambil daftar transaksi dengan filter
- `GET /{transaction_id}` - Ambil detail transaksi
- `PUT /{transaction_id}/status` - Update status transaksi
- `GET /stats/summary` - Ambil ringkasan statistik transaksi

## Discord Controllers

### 1. BotController (`bot_controller.py`)
**Tanggung Jawab**: Manajemen Discord Bot
- `POST /` - Buat konfigurasi Discord Bot baru
- `GET /` - Ambil daftar Discord Bot
- `GET /{bot_id}` - Ambil detail Discord Bot
- `PUT /{bot_id}` - Update Discord Bot
- `DELETE /{bot_id}` - Hapus Discord Bot
- `POST /{bot_id}/start` - Start Discord Bot
- `POST /{bot_id}/stop` - Stop Discord Bot
- `GET /{bot_id}/status` - Ambil status Discord Bot

### 2. UserController (`user_controller.py`)
**Tanggung Jawab**: Manajemen Discord User dan Wallet
- `GET /` - Ambil daftar Discord User
- `GET /{user_id}` - Ambil detail Discord User
- `PUT /{user_id}/verify` - Verifikasi Discord User
- `PUT /{user_id}/unverify` - Batalkan verifikasi Discord User
- `GET /{user_id}/wallet` - Ambil wallet Discord User
- `PUT /{user_id}/wallet/balance` - Update balance wallet
- `GET /stats/summary` - Ambil statistik Discord User

### 3. ProductController (`product_controller.py`)
**Tanggung Jawab**: Manajemen LiveStock dan World Configuration
- `GET /livestocks` - Ambil daftar LiveStock
- `POST /livestocks` - Buat LiveStock baru
- `GET /livestocks/{livestock_id}` - Ambil detail LiveStock
- `PUT /livestocks/{livestock_id}` - Update LiveStock
- `DELETE /livestocks/{livestock_id}` - Hapus LiveStock
- `GET /worlds` - Ambil daftar World Configuration
- `POST /worlds` - Buat World Configuration baru
- `GET /worlds/{world_id}` - Ambil detail World Configuration
- `PUT /worlds/{world_id}` - Update World Configuration
- `DELETE /worlds/{world_id}` - Hapus World Configuration

### 4. AnalyticsController (`analytics_controller.py`)
**Tanggung Jawab**: Analytics, logs, dan statistik Discord
- `GET /logs` - Ambil log Discord Bot
- `GET /commands/recent` - Ambil recent commands Discord Bot
- `GET /commands` - Ambil Discord commands dengan filter
- `GET /stats` - Ambil statistik Discord Bot
- `GET /stats/commands` - Ambil statistik command Discord
- `GET /stats/performance` - Ambil statistik performa Discord Bot

## Keuntungan Refactoring

### 1. Single Responsibility Principle (SRP)
- Setiap controller memiliki satu tanggung jawab yang jelas
- Lebih mudah untuk dipahami dan dipelihara
- Mengurangi coupling antar komponen

### 2. Maintainability
- Kode lebih terorganisir dan mudah dinavigasi
- Perubahan pada satu fitur tidak mempengaruhi fitur lain
- Debugging lebih mudah karena scope yang lebih kecil

### 3. Testability
- Unit testing lebih mudah karena controller lebih kecil
- Mock dependencies lebih sederhana
- Test coverage lebih baik

### 4. Scalability
- Mudah menambah fitur baru tanpa mengubah controller yang ada
- Tim development dapat bekerja parallel pada controller yang berbeda
- Deployment dapat dilakukan secara modular

### 5. Code Reusability
- Controller dapat digunakan kembali di berbagai konteks
- Service layer dapat dibagi antar controller
- Dependency injection lebih efektif

## Error Handling

Setiap controller dilengkapi dengan:
- **Try-catch blocks** untuk menangani exception
- **Logging** untuk debugging dan monitoring
- **Graceful degradation** untuk dependency yang tidak tersedia
- **Consistent error responses** menggunakan HTTPException

## Import Strategy

Controller menggunakan **defensive import strategy**:
```python
try:
    from app.models.discord import DiscordBot
except ImportError:
    DiscordBot = None
```

Ini memungkinkan controller tetap berfungsi meskipun beberapa dependency tidak tersedia.

## File Structure

```
app/
├── domains/
│   ├── admin/
│   │   └── controllers/
│   │       ├── __init__.py
│   │       ├── auth_controller.py
│   │       ├── admin_management_controller.py
│   │       ├── configuration_controller.py
│   │       ├── user_management_controller.py
│   │       ├── product_management_controller.py
│   │       ├── dashboard_controller.py
│   │       └── transaction_controller.py
│   └── discord/
│       └── controllers/
│           ├── __init__.py
│           ├── bot_controller.py
│           ├── user_controller.py
│           ├── product_controller.py
│           └── analytics_controller.py
```

## Migration Guide

### Untuk Developer
1. Import controller dari module yang sesuai
2. Gunakan dependency injection untuk service layer
3. Ikuti pattern yang sudah ada untuk consistency

### Untuk API Consumer
- Endpoint URLs tetap sama
- Response format tetap konsisten
- Authentication dan authorization tidak berubah

## Future Improvements

1. **Service Layer Refactoring**: Memecah service monolitik menjadi service yang lebih kecil
2. **Repository Pattern**: Implementasi repository pattern untuk data access
3. **Event-Driven Architecture**: Menggunakan events untuk komunikasi antar domain
4. **API Versioning**: Implementasi versioning untuk backward compatibility
5. **Rate Limiting**: Implementasi rate limiting per controller
6. **Caching Strategy**: Implementasi caching untuk endpoint yang sering diakses

## Conclusion

Refactoring ini meningkatkan kualitas kode secara signifikan dengan:
- Memisahkan concerns berdasarkan domain
- Meningkatkan maintainability dan testability
- Mempermudah development dan deployment
- Menyiapkan foundation untuk scaling aplikasi

Setiap controller sekarang memiliki fokus yang jelas dan dapat dikembangkan secara independen, membuat codebase lebih robust dan mudah dipelihara.
