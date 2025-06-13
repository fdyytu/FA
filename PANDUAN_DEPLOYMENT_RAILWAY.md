# 🚀 Panduan Deploy Aplikasi FA ke Railway

## Token Railway Anda
**Token Railway**: `930aa669-0a74-4055-bd1e-ed9bcc49d81d`

Token ini sudah dikonfigurasi sebagai SECRET_KEY untuk aplikasi Anda.

## ✅ Persiapan (Sudah Siap!)

Aplikasi Anda sudah dikonfigurasi dengan:
- ✅ `railway.json` - Konfigurasi Railway
- ✅ `Procfile` - Command startup: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- ✅ `requirements.txt` - Dependencies Python
- ✅ `runtime.txt` - Versi Python
- ✅ `.env.production` - Environment variables untuk production
- ✅ Health check endpoint di `/health`

## 🎯 Langkah Deploy ke Railway

### 1. Login ke Railway
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
3. Railway akan otomatis membuat database dan set `DATABASE_URL`

### 4. Set Environment Variables

Di tab **"Variables"**, tambahkan variabel berikut:

#### Security (WAJIB)
```
SECRET_KEY=930aa669-0a74-4055-bd1e-ed9bcc49d81d
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

#### Application Settings
```
APP_NAME=FA Application
DEBUG=False
LOG_LEVEL=INFO
ENVIRONMENT=production
```

#### Admin Settings (GANTI PASSWORD!)
```
ADMIN_USERNAME=admin
ADMIN_PASSWORD=password-yang-kuat-123!
```

#### External Services (Opsional - ganti dengan nilai asli)
```
DIGIFLAZZ_USERNAME=username-anda
DIGIFLAZZ_API_KEY=api-key-anda
MIDTRANS_SERVER_KEY=server-key-anda
MIDTRANS_CLIENT_KEY=client-key-anda
MIDTRANS_IS_PRODUCTION=false
```

**Catatan**: `DATABASE_URL` akan otomatis di-set oleh Railway PostgreSQL service.

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

### Endpoint yang Tersedia:
- **API Docs**: `https://your-app-name.up.railway.app/docs`
- **Health Check**: `https://your-app-name.up.railway.app/health`
- **Admin Panel**: `https://your-app-name.up.railway.app/static/admin/login.html`

## 🔧 Konfigurasi Tambahan

### Database Migration
Jika perlu menjalankan migration Alembic:
1. Di Railway dashboard, buka **"Settings"**
2. Tambahkan **"Deploy Command"**: 
   ```
   alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

### Auto-Deploy
Railway sudah otomatis setup auto-deploy. Setiap push ke branch main akan trigger deployment baru.

## 📊 Monitoring

### Melihat Logs
1. Di dashboard project, klik **"Deployments"**
2. Pilih deployment terbaru
3. Klik **"View Logs"**

### Health Check
Aplikasi memiliki health check di `/health` yang akan return:
```json
{
  "status": "healthy",
  "service": "FA API"
}
```

## 🐛 Troubleshooting

### Aplikasi Tidak Bisa Diakses
1. **Cek Logs**: Lihat error di deployment logs
2. **Cek Variables**: Pastikan semua environment variables ter-set
3. **Cek Database**: Pastikan PostgreSQL service aktif

### Database Connection Error
Pastikan `DATABASE_URL` format benar:
```
postgresql://username:password@host:port/database_name
```

### Build Failed
1. **Cek requirements.txt**: Pastikan semua dependencies valid
2. **Cek Python version**: Lihat `runtime.txt`
3. **Cek syntax**: Pastikan tidak ada error di kode

## 💰 Biaya Railway

### Free Tier
- $5 kredit gratis per bulan
- Cukup untuk aplikasi kecil-menengah
- PostgreSQL database included

### Upgrade
Jika kredit habis:
- **Developer Plan**: $5/bulan
- **Team Plan**: $20/bulan

## 🔄 Update Aplikasi

### Auto-Deploy (Recommended)
1. Push perubahan ke GitHub
2. Railway otomatis detect dan deploy
3. Monitor di dashboard

### Manual Deploy
1. Di Railway dashboard, klik **"Deployments"**
2. Klik **"Deploy Now"**

## 📝 Tips Penting

### 1. Security
- ✅ SECRET_KEY sudah di-set dengan token Railway Anda
- ✅ DEBUG=False untuk production
- ⚠️ Ganti ADMIN_PASSWORD dengan password yang kuat

### 2. Database
- Railway PostgreSQL sudah production-ready
- Backup otomatis tersedia
- Connection pooling sudah dihandle

### 3. Performance
- Railway auto-scale berdasarkan traffic
- Monitor resource usage di dashboard
- Optimize query database jika perlu

## 🎉 Selesai!

Aplikasi FA Anda sekarang sudah siap untuk di-deploy ke Railway!

**Checklist Terakhir:**
- [ ] Repository sudah di GitHub
- [ ] Environment variables sudah di-set di Railway
- [ ] PostgreSQL database sudah ditambahkan
- [ ] Domain sudah di-generate
- [ ] Health check berfungsi

---
*Panduan ini dibuat khusus untuk aplikasi FA dengan token Railway: 930aa669-0a74-4055-bd1e-ed9bcc49d81d*
