# 🚀 Panduan Lengkap Deploy ke Railway

## Apa itu Railway?
Railway adalah platform cloud modern yang memudahkan deployment aplikasi web. Cocok untuk aplikasi FastAPI seperti project ini.

## ✅ Persiapan (Sudah Siap!)
Project Anda sudah memiliki semua file yang diperlukan:
- ✅ `railway.json` - Konfigurasi Railway
- ✅ `Procfile` - Command untuk menjalankan aplikasi
- ✅ `requirements.txt` - Dependencies Python
- ✅ `runtime.txt` - Versi Python

## 🎯 Langkah-langkah Deploy

### 1. Persiapan Akun Railway
1. Buka https://railway.app
2. Klik **"Login"** dan pilih **"Login with GitHub"**
3. Authorize Railway untuk mengakses GitHub Anda

### 2. Deploy Project
1. Di dashboard Railway, klik **"New Project"**
2. Pilih **"Deploy from GitHub repo"**
3. Cari dan pilih repository **"FA"** Anda
4. Railway akan otomatis mendeteksi ini adalah aplikasi Python

### 3. Tambah Database PostgreSQL
1. Di project dashboard, klik **"+ New"**
2. Pilih **"Database"** → **"Add PostgreSQL"**
3. Railway akan otomatis membuat database dan set environment variable `DATABASE_URL`

### 4. Set Environment Variables
Di tab **"Variables"**, tambahkan:

```bash
# Security (WAJIB GANTI!)
SECRET_KEY=ganti-dengan-key-rahasia-yang-panjang-dan-acak
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
DEBUG=False
ENVIRONMENT=production

# Database (otomatis dari PostgreSQL service)
DATABASE_URL=(sudah otomatis ter-set)

# Opsional - Jika pakai external services
DIGIFLAZZ_USERNAME=username-anda
DIGIFLAZZ_API_KEY=api-key-anda
MIDTRANS_SERVER_KEY=server-key-anda
MIDTRANS_CLIENT_KEY=client-key-anda
```

### 5. Deploy!
1. Klik **"Deploy"** atau push ke GitHub
2. Railway akan otomatis build dan deploy
3. Tunggu hingga status menjadi **"Success"**
4. Klik **"View Logs"** untuk melihat proses deployment

## 🌐 Mengakses Aplikasi

Setelah deploy berhasil:
1. Di dashboard project, klik **"Settings"**
2. Scroll ke **"Domains"**
3. Klik **"Generate Domain"** untuk mendapat URL publik
4. URL akan berbentuk: `https://your-app-name.up.railway.app`

## 🔧 Konfigurasi Tambahan

### Auto-Deploy dari GitHub
Railway sudah otomatis setup auto-deploy. Setiap kali Anda push ke branch main, aplikasi akan otomatis ter-deploy ulang.

### Health Check
Aplikasi sudah dikonfigurasi dengan health check di endpoint `/health` (lihat `railway.json`).

### Database Migration
Jika perlu menjalankan migration Alembic:
1. Di Railway dashboard, buka **"Settings"**
2. Tambahkan **"Deploy Command"**: `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## 📊 Monitoring

### Melihat Logs
1. Di dashboard project, klik **"Deployments"**
2. Pilih deployment terbaru
3. Klik **"View Logs"** untuk melihat real-time logs

### Metrics
Railway menyediakan metrics dasar seperti:
- CPU usage
- Memory usage
- Network traffic
- Response time

## 💰 Biaya

### Free Tier
- $5 kredit gratis per bulan
- Cukup untuk aplikasi kecil-menengah
- PostgreSQL database included

### Upgrade
Jika kredit habis, bisa upgrade ke:
- **Developer Plan**: $5/bulan
- **Team Plan**: $20/bulan

## 🐛 Troubleshooting

### Aplikasi Tidak Bisa Diakses
1. **Cek Logs**: Lihat error di deployment logs
2. **Cek Variables**: Pastikan semua environment variables ter-set
3. **Cek Database**: Pastikan PostgreSQL service aktif

### Database Connection Error
```bash
# Pastikan DATABASE_URL format benar:
postgresql://username:password@host:port/database_name
```

### Build Failed
1. **Cek requirements.txt**: Pastikan semua dependencies valid
2. **Cek Python version**: Lihat `runtime.txt`
3. **Cek syntax**: Pastikan tidak ada error di kode

### Port Error
Railway otomatis set environment variable `$PORT`. Pastikan aplikasi menggunakan:
```python
# Di app/main.py
import os
port = int(os.environ.get("PORT", 8000))
```

## 🔄 Update Aplikasi

### Auto-Deploy (Recommended)
1. Push perubahan ke GitHub
2. Railway otomatis detect dan deploy
3. Monitor di dashboard

### Manual Deploy
1. Di Railway dashboard, klik **"Deployments"**
2. Klik **"Deploy Now"**

## 📝 Tips Penting

### 1. Environment Variables
- **JANGAN** commit file `.env` ke GitHub
- Set semua secrets di Railway dashboard
- Gunakan strong SECRET_KEY untuk production

### 2. Database
- Railway PostgreSQL sudah production-ready
- Backup otomatis tersedia
- Connection pooling sudah dihandle

### 3. Security
- HTTPS otomatis enabled
- Set `DEBUG=False` di production
- Gunakan strong passwords

### 4. Performance
- Railway auto-scale berdasarkan traffic
- Monitor resource usage di dashboard
- Optimize query database jika perlu

## 🎉 Selesai!

Aplikasi FastAPI Anda sekarang sudah live di Railway! 

**URL Aplikasi**: `https://your-app-name.up.railway.app`
**API Docs**: `https://your-app-name.up.railway.app/docs`
**Health Check**: `https://your-app-name.up.railway.app/health`

## 📞 Bantuan Lebih Lanjut

- **Railway Docs**: https://docs.railway.app
- **Railway Discord**: https://discord.gg/railway
- **FastAPI Docs**: https://fastapi.tiangolo.com

---
*Panduan ini dibuat khusus untuk project FA dengan konfigurasi yang sudah ada.*
