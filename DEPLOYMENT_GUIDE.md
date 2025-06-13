# Panduan Deploy Backend FastAPI

## Platform Deployment Gratis Terbaik

### 1. **Railway** (Paling Direkomendasikan) ⭐
- **Gratis**: $5 kredit bulanan
- **Database**: PostgreSQL gratis included
- **Redis**: Add-on tersedia
- **Auto-deploy**: Dari GitHub
- **URL**: https://railway.app

#### Langkah Deploy ke Railway:
1. Daftar di https://railway.app dengan GitHub
2. Klik "New Project" → "Deploy from GitHub repo"
3. Pilih repository ini
4. Railway akan otomatis detect FastAPI
5. Tambahkan PostgreSQL service
6. Set environment variables dari .env.example
7. Deploy otomatis!

### 2. **Render** 
- **Gratis**: Web service gratis (sleep setelah 15 menit idle)
- **Database**: PostgreSQL gratis 90 hari
- **URL**: https://render.com

#### Langkah Deploy ke Render:
1. Daftar di https://render.com
2. Connect GitHub repository
3. Pilih "Web Service"
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Tambahkan PostgreSQL database
7. Set environment variables

### 3. **Fly.io**
- **Gratis**: 3 shared-cpu VMs
- **Database**: PostgreSQL dengan volume gratis
- **URL**: https://fly.io

#### Langkah Deploy ke Fly.io:
1. Install flyctl: `curl -L https://fly.io/install.sh | sh`
2. Login: `flyctl auth login`
3. Launch app: `flyctl launch`
4. Deploy: `flyctl deploy`

### 4. **Heroku** (Berbayar)
- **Tidak gratis lagi**, tapi bisa pakai student pack
- **URL**: https://heroku.com

## Environment Variables yang Diperlukan

Untuk semua platform, set environment variables berikut:

```bash
# Database (akan otomatis di Railway/Render)
DATABASE_URL=postgresql://user:pass@host:port/dbname

# Security
SECRET_KEY=your-super-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
DEBUG=False
ENVIRONMENT=production
ALLOWED_HOSTS=["your-domain.com"]

# External Services (opsional)
DIGIFLAZZ_USERNAME=your-username
DIGIFLAZZ_API_KEY=your-api-key
MIDTRANS_SERVER_KEY=your-server-key
MIDTRANS_CLIENT_KEY=your-client-key

# Redis (jika diperlukan)
REDIS_URL=redis://host:port/0
```

## File yang Sudah Disiapkan untuk Deployment

1. **Procfile** - Untuk Heroku/Railway
2. **railway.json** - Konfigurasi Railway
3. **runtime.txt** - Versi Python
4. **requirements.txt** - Dependencies

## Tips Deployment

1. **Gunakan Railway** untuk kemudahan dan fitur lengkap
2. **Set DEBUG=False** di production
3. **Gunakan PostgreSQL** bukan SQLite
4. **Enable HTTPS** (otomatis di semua platform)
5. **Monitor logs** untuk debugging
6. **Backup database** secara berkala

## Troubleshooting

### Error "Port already in use"
- Pastikan menggunakan `--port $PORT` di start command

### Database connection error
- Periksa DATABASE_URL environment variable
- Pastikan PostgreSQL service aktif

### Import error
- Periksa requirements.txt
- Pastikan semua dependencies terinstall

### 502 Bad Gateway
- Periksa health check endpoint
- Pastikan aplikasi bind ke 0.0.0.0

## Monitoring & Maintenance

1. **Logs**: Monitor aplikasi logs di dashboard platform
2. **Metrics**: Enable monitoring di platform
3. **Backup**: Setup automated database backup
4. **Updates**: Deploy otomatis dari GitHub push

## Estimasi Biaya

- **Railway**: Gratis ($5 kredit) → $5-20/bulan
- **Render**: Gratis → $7/bulan (database)
- **Fly.io**: Gratis → $5-15/bulan
- **Heroku**: $7/bulan minimum

**Rekomendasi**: Mulai dengan Railway untuk development, upgrade sesuai kebutuhan.
