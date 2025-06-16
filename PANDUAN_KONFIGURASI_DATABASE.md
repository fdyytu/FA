# Panduan Konfigurasi Database PostgreSQL Railway

## 📋 Ringkasan Konfigurasi

Aplikasi FA telah dikonfigurasi untuk menggunakan PostgreSQL Railway dengan pengaturan berikut:

### 🔗 URL Database yang Tersedia

1. **External URL (Digunakan saat ini)**:
   ```
   postgresql://postgres:qHWjVgbrmeenNJpekWtqarXQeSvyzNsU@trolley.proxy.rlwy.net:52538/railway
   ```

2. **Internal URL (Untuk deployment di Railway)**:
   ```
   postgresql://postgres:qHWjVgbrmeenNJpekWtqarXQeSvyzNsU@postgres.railway.internal:5432/railway
   ```

### 🎯 Mana yang Harus Digunakan?

| Konteks | URL yang Digunakan | Alasan |
|---------|-------------------|---------|
| **Development Lokal** | External URL | Dapat diakses dari luar Railway |
| **Deployment di Railway** | Internal URL | Lebih cepat dan aman (komunikasi internal) |
| **Testing dari luar Railway** | External URL | Satu-satunya yang dapat diakses |

## ⚙️ File yang Telah Dikonfigurasi

### 1. `.env` (File Utama)
```env
DATABASE_URL=postgresql://postgres:qHWjVgbrmeenNJpekWtqarXQeSvyzNsU@trolley.proxy.rlwy.net:52538/railway
```

### 2. `app/infrastructure/config/settings.py`
- Otomatis mendeteksi PostgreSQL dari DATABASE_URL
- Menggunakan connection pooling untuk performa optimal
- Pool size: 5, Max overflow: 10

### 3. `app/core/database.py`
- Engine PostgreSQL dengan konfigurasi optimal
- Session management yang proper
- Error handling yang baik

## 🧪 Status Testing

✅ **Koneksi Database**: Berhasil  
✅ **CREATE TABLE**: Berhasil  
✅ **INSERT Data**: Berhasil  
✅ **SELECT Data**: Berhasil  
✅ **Cleanup**: Berhasil  

## 🚀 Cara Mengganti URL Database

### Untuk Development Lokal:
```bash
# Edit file .env
DATABASE_URL=postgresql://postgres:qHWjVgbrmeenNJpekWtqarXQeSvyzNsU@trolley.proxy.rlwy.net:52538/railway
```

### Untuk Deployment Railway:
```bash
# Edit file .env atau set di Railway Dashboard
DATABASE_URL=postgresql://postgres:qHWjVgbrmeenNJpekWtqarXQeSvyzNsU@postgres.railway.internal:5432/railway
```

## 🔧 Troubleshooting

### Error: "could not translate host name"
- **Penyebab**: Menggunakan internal URL di luar Railway
- **Solusi**: Gunakan external URL untuk development lokal

### Error: "Connection timeout"
- **Penyebab**: Network issue atau URL salah
- **Solusi**: Cek koneksi internet dan pastikan URL benar

### Error: "Authentication failed"
- **Penyebab**: Password atau username salah
- **Solusi**: Verifikasi credentials di Railway Dashboard

## 📝 Catatan Penting

1. **Keamanan**: Jangan commit file `.env` ke repository public
2. **Performance**: Internal URL lebih cepat untuk production
3. **Monitoring**: Gunakan Railway Dashboard untuk monitoring database
4. **Backup**: Railway otomatis backup database secara berkala

## 🔄 Migrasi Database

Untuk menjalankan migrasi database:

```bash
# Install dependencies
pip install -r requirements.txt

# Jalankan migrasi Alembic
alembic upgrade head

# Atau jalankan auto create tables
python3 auto_create_tables.py
```

## 📞 Support

Jika mengalami masalah:
1. Cek Railway Dashboard untuk status database
2. Verifikasi environment variables
3. Test koneksi dengan: `python3 check_postgresql_connection.py`
