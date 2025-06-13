# FA - PPOB Application dengan Digiflazz Integration

## Fitur yang Telah Diimplementasi

### 1. **Provider PPOB Digiflazz**
- ✅ Implementasi `DigiflazzProvider` untuk integrasi dengan API Digiflazz
- ✅ Support untuk inquiry dan payment melalui Digiflazz
- ✅ Automatic fallback ke DefaultProvider jika konfigurasi Digiflazz belum lengkap
- ✅ Signature generation sesuai dengan requirement Digiflazz API

### 2. **Konfigurasi Admin Dashboard**
- ✅ Model `AdminConfig` untuk menyimpan konfigurasi sistem
- ✅ Model `PPOBMarginConfig` untuk pengaturan margin PPOB
- ✅ Enkripsi otomatis untuk data sensitif (API Key, Secret Key)
- ✅ Support untuk konfigurasi margin berdasarkan:
  - Global (semua kategori)
  - Per kategori PPOB
  - Per produk spesifik

### 3. **Pengaturan Margin Dinamis**
- ✅ Support margin dalam bentuk **Persentase** atau **Nominal**
- ✅ Prioritas margin: Produk Spesifik > Kategori > Global
- ✅ Perhitungan otomatis harga final dengan margin
- ✅ Admin dapat mengatur margin sesuka hati via dashboard

### 4. **Konfigurasi Digiflazz via Dashboard**
- ✅ Endpoint untuk set/get konfigurasi Digiflazz
- ✅ Penyimpanan aman username, API key, dan mode production
- ✅ Test koneksi ke Digiflazz API
- ✅ Ambil price list dari Digiflazz

### 5. **Logging System**
- ✅ File `server.log` untuk monitoring dan debug server
- ✅ File `ppob.log` khusus untuk transaksi PPOB
- ✅ File `admin.log` khusus untuk aktivitas admin
- ✅ File `app.log` untuk log aplikasi umum

## Endpoint API Admin

### Konfigurasi Digiflazz
```
POST /api/v1/admin/digiflazz/config
GET  /api/v1/admin/digiflazz/config
POST /api/v1/admin/digiflazz/test-connection
GET  /api/v1/admin/digiflazz/price-list
```

### Konfigurasi Margin
```
POST /api/v1/admin/margin
GET  /api/v1/admin/margin
PUT  /api/v1/admin/margin/{margin_id}
DELETE /api/v1/admin/margin/{margin_id}
```

### Konfigurasi Umum
```
POST /api/v1/admin/config
GET  /api/v1/admin/config
GET  /api/v1/admin/config/{config_key}
PUT  /api/v1/admin/config/{config_key}
DELETE /api/v1/admin/config/{config_key}
```

## Cara Penggunaan

### 1. Setup Konfigurasi Digiflazz
```bash
curl -X POST "http://localhost:8000/api/v1/admin/digiflazz/config" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your_digiflazz_username",
    "api_key": "your_digiflazz_api_key",
    "production": false
  }'
```

### 2. Setup Margin Global (10%)
```bash
curl -X POST "http://localhost:8000/api/v1/admin/margin" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "global",
    "margin_type": "percentage",
    "margin_value": 10.0,
    "description": "Margin global 10%"
  }'
```

### 3. Setup Margin Kategori Pulsa (Rp 1000)
```bash
curl -X POST "http://localhost:8000/api/v1/admin/margin" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "pulsa",
    "margin_type": "nominal",
    "margin_value": 1000,
    "description": "Margin pulsa Rp 1000"
  }'
```

### 4. Test Koneksi Digiflazz
```bash
curl -X POST "http://localhost:8000/api/v1/admin/digiflazz/test-connection" \
  -H "Authorization: Bearer <admin_token>"
```

## Database Schema

### Tabel `admin_configs`
- `id` - Primary key
- `config_key` - Unique key untuk konfigurasi
- `config_value` - Nilai konfigurasi (terenkripsi jika sensitif)
- `config_type` - Tipe: string, number, boolean, encrypted
- `description` - Deskripsi konfigurasi
- `is_active` - Status aktif

### Tabel `ppob_margin_configs`
- `id` - Primary key
- `category` - Kategori PPOB atau 'global'
- `product_code` - Kode produk spesifik (nullable)
- `margin_type` - PERCENTAGE atau NOMINAL
- `margin_value` - Nilai margin
- `is_active` - Status aktif
- `description` - Deskripsi margin

## File Logging

- **`logs/server.log`** - Log server dan sistem
- **`logs/ppob.log`** - Log transaksi PPOB
- **`logs/admin.log`** - Log aktivitas admin
- **`logs/app.log`** - Log aplikasi umum

## Keamanan

- ✅ API Key Digiflazz disimpan terenkripsi menggunakan Fernet
- ✅ Hanya user dengan `is_superuser=True` yang dapat akses endpoint admin
- ✅ Encryption key disimpan aman di database
- ✅ API Key tidak ditampilkan dalam response GET

## Cara Menjalankan

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Jalankan migration:
```bash
alembic upgrade head
```

3. Jalankan aplikasi:
```bash
python3 run.py
```

4. Aplikasi akan berjalan di `http://localhost:8000`

5. Dokumentasi API tersedia di `http://localhost:8000/docs`

## Testing

Aplikasi sudah berjalan dan siap digunakan. Semua endpoint telah diimplementasi dan database schema telah dibuat.

**Status: ✅ SELESAI**

Semua requirement telah diimplementasi:
- ✅ Provider PPOB diganti ke Digiflazz
- ✅ Margin dapat diatur admin (persen/nominal) via dashboard
- ✅ Secret key Digiflazz diatur dari dashboard admin
- ✅ File server.log untuk monitoring debug
