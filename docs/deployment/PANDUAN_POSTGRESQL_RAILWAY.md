# 🚀 PANDUAN KONEKSI POSTGRESQL RAILWAY & AUTO-CREATE TABEL

## 📋 Ringkasan Status

✅ **Backend sudah siap untuk PostgreSQL Railway**
✅ **Auto-create tabel sudah diimplementasi**
✅ **Health check database sudah tersedia**
✅ **Fallback ke SQLite untuk development**

## 🔍 Cara Mengecek Koneksi PostgreSQL Railway

### 1. Menggunakan Script Checker
```bash
# Jalankan script untuk cek koneksi PostgreSQL
python3 check_postgresql_connection.py
```

### 2. Menggunakan Health Endpoint
```bash
# Cek status database melalui API
curl http://localhost:8000/health
```

### 3. Menggunakan Script Auto-Create Tabel
```bash
# Test pembuatan tabel otomatis
python3 auto_create_tables.py
```

## 🐘 Setup PostgreSQL Railway

### 1. Menambahkan PostgreSQL Service di Railway
1. Buka dashboard Railway project Anda
2. Klik "Add Service" → "Database" → "PostgreSQL"
3. Railway akan otomatis membuat DATABASE_URL environment variable

### 2. Verifikasi Environment Variables
Railway akan otomatis menambahkan:
```
DATABASE_URL=postgresql://username:password@host:port/database
```

### 3. Restart Aplikasi
Setelah PostgreSQL service ditambahkan, restart aplikasi:
```bash
# Railway akan otomatis restart, atau manual:
railway up
```

## 🏗️ Auto-Create Tabel

### Fitur yang Sudah Diimplementasi:

1. **Startup Auto-Create**: Tabel dibuat otomatis saat aplikasi startup
2. **Multi-Database Support**: Mendukung PostgreSQL dan SQLite
3. **Model Detection**: Otomatis import semua model yang tersedia
4. **Error Handling**: Aplikasi tetap jalan meski ada model yang error

### Model yang Didukung:
- ✅ DiscordConfig
- ✅ Admin  
- ✅ Product
- ✅ User
- ✅ Voucher
- ⚠️ Wallet (perlu perbaikan model)
- ⚠️ Analytics (perlu perbaikan model)

## 📊 Monitoring Database

### Health Check Response:
```json
{
  "status": "healthy",
  "service": "FA API", 
  "database": {
    "status": "healthy",
    "type": "PostgreSQL", // atau "SQLite"
    "url": "postgresql://...",
    "tables_count": 5,
    "connection": "ok"
  }
}
```

### Log Monitoring:
```bash
# Cek log aplikasi
tail -f server.log

# Cek log database initialization
grep "database" server.log
```

## 🔧 Troubleshooting

### 1. DATABASE_URL Tidak Ditemukan
**Masalah**: `DATABASE_URL tidak ditemukan di environment variables`

**Solusi**:
- Pastikan PostgreSQL service sudah ditambahkan di Railway
- Restart aplikasi setelah menambahkan service
- Cek environment variables di Railway dashboard

### 2. Koneksi PostgreSQL Gagal
**Masalah**: `Error koneksi SQLAlchemy`

**Solusi**:
```bash
# Test koneksi manual
python3 check_postgresql_connection.py

# Cek log detail
grep "Error" server.log
```

### 3. Tabel Tidak Terbuat
**Masalah**: `Tables created successfully! Total: 0`

**Solusi**:
- Cek import model di log
- Pastikan model class sudah benar
- Jalankan script manual: `python3 auto_create_tables.py`

### 4. Model Import Error
**Masalah**: `cannot import name 'ModelName'`

**Solusi**:
- Cek file model di `app/domains/*/models/`
- Pastikan class name sesuai dengan import
- Model yang error tidak akan mengganggu yang lain

## 🎯 Cara Mengecek Status Koneksi

### 1. Cek Environment Variables
```bash
# Di Railway console atau local
echo $DATABASE_URL
```

### 2. Cek Aplikasi Logs
```bash
# Cari log database initialization
grep -i "database\|postgresql\|sqlite" server.log
```

### 3. Test API Endpoints
```bash
# Health check
curl http://localhost:8000/health

# Root endpoint
curl http://localhost:8000/
```

### 4. Cek Database Tables
```bash
# Menggunakan script checker
python3 check_postgresql_connection.py

# Atau manual query (jika PostgreSQL)
psql $DATABASE_URL -c "\dt"
```

## 📈 Monitoring Production

### Railway Dashboard:
1. **Metrics**: CPU, Memory, Network usage
2. **Logs**: Real-time application logs  
3. **Environment**: DATABASE_URL dan variables lain
4. **Database**: PostgreSQL metrics dan connection info

### Health Endpoints:
- `GET /health` - Status database dan Discord bot
- `GET /` - Basic service info
- `GET /docs` - API documentation

## 🔄 Alur Kerja Auto-Create Tabel

1. **Aplikasi Startup** → `main.py:startup_event()`
2. **Import Models** → Semua model di `app/domains/*/models/`
3. **Detect Database** → PostgreSQL atau SQLite
4. **Create Tables** → `Base.metadata.create_all()`
5. **Verify Tables** → Count dan list tabel
6. **Log Results** → Info jumlah tabel yang dibuat

## 🚀 Deployment ke Railway

### 1. Push ke Repository
```bash
git add .
git commit -m "Add PostgreSQL Railway support & auto-create tables"
git push origin main
```

### 2. Deploy di Railway
```bash
# Atau menggunakan Railway CLI
railway up
```

### 3. Tambahkan PostgreSQL Service
1. Railway Dashboard → Add Service → PostgreSQL
2. Wait for DATABASE_URL to be set
3. Restart application

### 4. Verifikasi Deployment
```bash
# Cek health endpoint
curl https://your-app.railway.app/health

# Cek logs
railway logs
```

## ✅ Checklist Verifikasi

- [ ] PostgreSQL service ditambahkan di Railway
- [ ] DATABASE_URL environment variable tersedia
- [ ] Aplikasi berhasil startup tanpa error database
- [ ] Health endpoint menunjukkan database "healthy"
- [ ] Tabel berhasil dibuat (tables_count > 0)
- [ ] Log menunjukkan "PostgreSQL tables created"

## 📞 Support

Jika ada masalah:
1. Cek log aplikasi: `railway logs` atau `cat server.log`
2. Test script: `python3 check_postgresql_connection.py`
3. Cek health endpoint: `curl /health`
4. Verifikasi environment variables di Railway dashboard
