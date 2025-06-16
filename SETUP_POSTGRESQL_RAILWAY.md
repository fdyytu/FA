# Setup PostgreSQL Railway Auto-Create Tables

## 📋 Ringkasan

Aplikasi FA telah dikonfigurasi untuk **otomatis membuat semua tabel database** saat startup. Tidak perlu setup manual tabel di PostgreSQL Railway.

## 🚀 Yang Harus Anda Lakukan di PostgreSQL Railway

### 1. Buat Database PostgreSQL di Railway
1. Login ke [Railway.app](https://railway.app)
2. Buat project baru atau gunakan project yang sudah ada
3. Tambahkan **PostgreSQL** service
4. Railway akan otomatis generate database credentials

### 2. Dapatkan Database URL
Setelah PostgreSQL service dibuat, Railway akan memberikan:
- **DATABASE_URL** (format: `postgresql://username:password@host:port/database`)
- **PGHOST**, **PGPORT**, **PGUSER**, **PGPASSWORD**, **PGDATABASE**

### 3. Set Environment Variables
Di Railway project settings, tambahkan environment variable:
```
DATABASE_URL=postgresql://username:password@host:port/database
```

### 4. Deploy Aplikasi
Deploy aplikasi FA ke Railway. Saat aplikasi startup, akan otomatis:
- ✅ Koneksi ke PostgreSQL Railway
- ✅ Import semua model database (19 models)
- ✅ Membuat semua tabel yang dibutuhkan (20+ tables)
- ✅ Siap digunakan!

## 📊 Tabel yang Akan Dibuat Otomatis

Aplikasi akan membuat **20+ tabel** secara otomatis:

### 👤 User & Auth Tables
- `users` - Data pengguna
- `admins` - Data admin
- `admin_configs` - Konfigurasi admin
- `admin_audit_logs` - Log aktivitas admin
- `admin_notification_settings` - Setting notifikasi admin

### 💰 Wallet & Transaction Tables
- `wallet_transactions` - Transaksi wallet
- `transfers` - Transfer antar user
- `topup_requests` - Permintaan top up

### 🛍️ Product & PPOB Tables
- `products` - Data produk
- `ppob_transactions` - Transaksi PPOB
- `ppob_products` - Produk PPOB
- `ppob_margin_configs` - Konfigurasi margin PPOB

### 🎫 Voucher Tables
- `vouchers` - Data voucher
- `voucher_usages` - Penggunaan voucher

### 📊 Analytics Tables
- `analytics_events` - Event analytics
- `product_analytics` - Analytics produk
- `voucher_analytics` - Analytics voucher
- `dashboard_metrics` - Metrics dashboard

### 🤖 Discord Tables
- `discord_configs` - Konfigurasi Discord bot

## 🔧 Cara Kerja Auto-Setup

### 1. Saat Aplikasi Startup
```python
@app.on_event("startup")
async def startup_event():
    # Auto-create database tables
    await auto_create_database_tables()
    # Initialize Discord bot
    # ...
```

### 2. Function Auto-Create Tables
```python
async def auto_create_database_tables():
    # Import semua model (19 models)
    # Create all tables menggunakan SQLAlchemy
    # Verify tables created
    # Log hasil
```

### 3. Models yang Diimpor
- **Discord**: DiscordConfig
- **Wallet**: WalletTransaction, Transfer, TopUpRequest  
- **Admin**: Admin, AdminConfig, PPOBMarginConfig, AdminAuditLog, AdminNotificationSetting
- **Product**: Product
- **Auth**: User
- **Voucher**: Voucher, VoucherUsage
- **Analytics**: AnalyticsEvent, ProductAnalytics, VoucherAnalytics, DashboardMetrics
- **PPOB**: PPOBTransaction, PPOBProduct

## ✅ Verifikasi Setup

### 1. Check Logs Aplikasi
Saat startup, akan muncul log:
```
INFO:main:Importing database models...
INFO:main:Models imported: ['DiscordConfig', 'WalletTransaction', ...]
INFO:main:Creating database tables...
INFO:main:PostgreSQL tables created: 20 tables
INFO:main:Database initialization completed successfully
```

### 2. Check Health Endpoint
Akses `/health` endpoint untuk melihat status database:
```json
{
  "status": "healthy",
  "database": {
    "status": "healthy", 
    "type": "PostgreSQL",
    "tables_count": 20,
    "connection": "ok"
  }
}
```

### 3. Manual Check (Opsional)
Jika ingin check manual, bisa jalankan script:
```bash
python3 auto_create_tables.py
```

## 🚨 Troubleshooting

### Error: "No module named 'sqlalchemy'"
```bash
pip install -r requirements.txt
```

### Error: Database Connection Failed
- Pastikan DATABASE_URL benar
- Check PostgreSQL service di Railway aktif
- Verify network connectivity

### Error: Import Model Failed
- Check semua file model ada
- Verify Python path
- Check dependencies

## 📝 Catatan Penting

1. **Tidak perlu setup manual tabel** - semua otomatis
2. **Aman untuk re-deploy** - `create_all()` tidak akan overwrite data existing
3. **Support SQLite dan PostgreSQL** - auto-detect dari DATABASE_URL
4. **Logging lengkap** - semua proses tercatat di log
5. **Error handling** - aplikasi tetap jalan meski ada error database

## 🎯 Kesimpulan

Dengan setup ini, Anda hanya perlu:
1. ✅ Buat PostgreSQL di Railway
2. ✅ Set DATABASE_URL environment variable  
3. ✅ Deploy aplikasi
4. ✅ **Selesai!** - Semua tabel otomatis terbuat

**Tidak ada setup manual yang diperlukan di PostgreSQL Railway!**
