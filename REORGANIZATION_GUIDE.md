# Panduan Reorganisasi File FA Application

## Struktur Baru

Reorganisasi ini dilakukan untuk meningkatkan organisasi file dan memudahkan maintenance:

### 📁 config/
Berisi semua file konfigurasi aplikasi:
- `.env*` - File environment variables
- `alembic.ini` - Konfigurasi Alembic untuk database migration
- `railway.json` - Konfigurasi deployment Railway
- `nixpacks.toml` - Konfigurasi build Nixpacks

### 📁 deployment/
Berisi file-file yang berkaitan dengan deployment:
- `Dockerfile` - Container configuration
- `Procfile` - Process configuration untuk Heroku/Railway
- `runtime.txt` - Python runtime specification

### 📁 database/
Berisi semua file yang berkaitan dengan database:
- `alembic/` - Alembic migration files (dipindahkan dari root)
- `migrations/` - Database migration scripts (dipindahkan dari root)

### 📁 docs/
Berisi semua dokumentasi termasuk file reorganisasi yang dipindahkan dari root:
- `REORGANIZATION_*.md` - Dokumentasi reorganisasi sebelumnya
- File dokumentasi API dan deployment lainnya

## Perubahan Path

### File Konfigurasi
- **Sebelum**: `.env` di root
- **Sesudah**: `config/.env`
- **Update**: `app/infrastructure/config/settings.py` telah diperbarui

### Database Migration
- **Sebelum**: `alembic/` dan `migrations/` di root
- **Sesudah**: `database/alembic/` dan `database/migrations/`
- **Update**: `config/alembic.ini` telah diperbarui

### File Deployment
- **Sebelum**: `Dockerfile`, `Procfile`, `runtime.txt` di root
- **Sesudah**: `deployment/Dockerfile`, `deployment/Procfile`, `deployment/runtime.txt`

## Cara Menjalankan Setelah Reorganisasi

### Development
```bash
# Pastikan file .env ada di folder config/
cp config/.env.example config/.env

# Jalankan aplikasi
python main.py
```

### Database Migration
```bash
# Jalankan dari root directory
alembic -c config/alembic.ini upgrade head
```

### Docker Build
```bash
# Build dengan Dockerfile yang baru
docker build -f deployment/Dockerfile -t fa-app .
```

## Manfaat Reorganisasi

1. **Pemisahan Concern**: File dikelompokkan berdasarkan fungsi
2. **Kemudahan Maintenance**: Lebih mudah menemukan file yang dibutuhkan
3. **Struktur yang Konsisten**: Mengikuti best practice project structure
4. **Deployment yang Lebih Bersih**: File deployment terpisah dari kode aplikasi

## Catatan Penting

- Semua referensi path telah diperbarui
- Aplikasi tetap berjalan normal setelah reorganisasi
- Struktur domain di folder `app/` tidak berubah
- File `main.py` tetap sebagai entry point utama
