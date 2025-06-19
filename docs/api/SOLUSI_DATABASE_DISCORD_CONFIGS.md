# Solusi Error: no such table: discord_configs

## Deskripsi Masalah

Error yang terjadi:
```
2025-06-14 23:42:46 - app.api.v1.endpoints.discord_config - ERROR - Error creating Discord config: (sqlite3.OperationalError) no such table: discord_configs
```

## Penyebab Masalah

1. **Database belum diinisialisasi**: Tabel `discord_configs` belum dibuat di database SQLite
2. **Migrasi Alembic bermasalah**: Ada multiple head revisions yang menyebabkan migrasi tidak bisa dijalankan
3. **Model tidak teregistrasi**: Model SQLAlchemy belum diregistrasi dengan Base metadata

## Solusi yang Diterapkan

### 1. Inisialisasi Database Manual

Dibuat script `init_database.py` yang melakukan:
- Import semua model SQLAlchemy yang diperlukan
- Registrasi model dengan Base metadata
- Membuat semua tabel menggunakan `Base.metadata.create_all()`
- Verifikasi tabel `discord_configs` berhasil dibuat

### 2. Script Inisialisasi Database

```bash
# Jalankan script inisialisasi
python3 init_database.py
```

Output yang diharapkan:
```
🔄 Memulai inisialisasi database...
📦 Mengimpor model database...
✅ Wallet models imported
✅ Admin models imported  
✅ Product models imported
🏗️  Membuat tabel database...
🔍 Memverifikasi tabel discord_configs...
✅ Tabel discord_configs berhasil dibuat!
📋 Struktur tabel discord_configs:
   - id INTEGER (nullable: False)
   - name VARCHAR(100) (nullable: False)
   - token TEXT (nullable: False)
   - guild_id VARCHAR(50) (nullable: True)
   - command_prefix VARCHAR(10) (nullable: False)
   - is_active BOOLEAN (nullable: True)
   - is_encrypted BOOLEAN (nullable: True)
   - created_at DATETIME (nullable: True)
   - updated_at DATETIME (nullable: True)
📊 Total tabel dalam database: 2
   - alembic_version
   - discord_configs
🎉 Inisialisasi database berhasil!
```

## Verifikasi Solusi

### 1. Test Endpoint Discord Config

```bash
# Test membuat konfigurasi Discord
curl -X POST http://localhost:8000/api/v1/discord/config   -H "Content-Type: application/json"   -d '{
    "name": "Test Config",
    "token": "MTIzNDU2Nzg5MDEyMzQ1Njc4OTAxMjM0NTY3ODkwMTIzNDU2Nzg5MDEyMzQ1Njc4OTA",
    "guild_id": "123456789",
    "command_prefix": "!",
    "is_active": true
  }'
```

Response sukses:
```json
{
  "success": true,
  "message": "Konfigurasi Discord berhasil dibuat",
  "data": {
    "name": "Test Config",
    "token": "Z0FBQUFBQm...PQ==",
    "guild_id": "123456789",
    "command_prefix": "!",
    "is_active": true,
    "id": 1,
    "is_encrypted": true,
    "created_at": "2025-06-14T23:49:30",
    "updated_at": null
  }
}
```

### 2. Test Endpoint Get Active Config

```bash
# Test mendapatkan konfigurasi aktif
curl -X GET http://localhost:8000/api/v1/discord/config/active
```

Response sukses:
```json
{
  "success": true,
  "data": {
    "name": "Test Config",
    "token": "Z0FBQUFBQm...PQ==",
    "guild_id": "123456789",
    "command_prefix": "!",
    "is_active": true,
    "id": 1,
    "is_encrypted": true,
    "created_at": "2025-06-14T23:49:30",
    "updated_at": null
  }
}
```

### 3. Test Bot Status

```bash
# Test status bot
curl -X GET http://localhost:8000/api/v1/bot/status
```

Response sukses:
```json
{
  "success": true,
  "data": {
    "status": "not_initialized",
    "is_running": false,
    "guilds": 0,
    "users": 0,
    "latency": 0,
    "manager_initialized": false,
    "config_source": null,
    "token_configured": true,
    "token_sources": {
      "environment": false,
      "database": true
    },
    "environment": {
      "command_prefix": "!",
      "guild_id": null
    }
  }
}
```

## Struktur Database

Tabel `discord_configs` yang dibuat memiliki struktur:

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| id | INTEGER | No | - |
| name | VARCHAR(100) | No | "Default Config" |
| token | TEXT | No | - |
| guild_id | VARCHAR(50) | Yes | - |
| command_prefix | VARCHAR(10) | No | "!" |
| is_active | BOOLEAN | Yes | true |
| is_encrypted | BOOLEAN | Yes | true |
| created_at | DATETIME | Yes | now() |
| updated_at | DATETIME | Yes | - |

## Langkah Deployment

### 1. Development Environment

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Inisialisasi database
python3 init_database.py

# 3. Jalankan aplikasi
python3 main.py
```

### 2. Production Environment

```bash
# 1. Set environment variables
export DATABASE_URL="sqlite:///./fa_database.db"

# 2. Inisialisasi database
python3 init_database.py

# 3. Jalankan aplikasi
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Catatan Penting

1. **Backup Database**: Selalu backup database sebelum menjalankan script inisialisasi
2. **Environment Variables**: Pastikan `DATABASE_URL` sudah dikonfigurasi dengan benar
3. **Permissions**: Pastikan aplikasi memiliki permission untuk membuat/menulis file database
4. **Token Security**: Token Discord akan dienkripsi secara otomatis saat disimpan

## Troubleshooting

### Error: "Database file tidak ditemukan"
- Pastikan path database dalam `DATABASE_URL` dapat diakses
- Periksa permission direktori

### Error: "Import model gagal"
- Pastikan semua dependencies sudah terinstall
- Periksa struktur direktori aplikasi

### Error: "Tabel masih tidak ditemukan"
- Jalankan ulang script `init_database.py`
- Periksa log error untuk detail masalah

## Status Solusi

✅ **BERHASIL DISELESAIKAN**

- Tabel `discord_configs` berhasil dibuat
- Endpoint Discord config berfungsi normal
- Aplikasi dapat menyimpan dan mengambil konfigurasi Discord
- Bot status endpoint berfungsi dengan baik
