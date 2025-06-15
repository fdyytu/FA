# 🚀 Panduan Lengkap Deployment ke Railway

## Daftar Isi
1. [Persiapan](#persiapan)
2. [Deployment ke Railway](#deployment-ke-railway)
3. [Troubleshooting](#troubleshooting)
4. [Checklist Deployment](#checklist-deployment)

## Persiapan

### File yang Diperlukan (✅ Sudah Tersedia)
- ✅ `railway.json` - Konfigurasi Railway
- ✅ `Procfile` - Command startup: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- ✅ `requirements.txt` - Dependencies Python
- ✅ `nixpacks.toml` - Konfigurasi build
- ✅ `.env.railway.example` - Template environment variables

### Environment Variables yang Diperlukan
```bash
# Database
DATABASE_URL=${{ Postgres.DATABASE_URL }}

# Security
SECRET_KEY=your-secret-key-here

# Application
DEBUG=False
ENVIRONMENT=production

# External Services
DIGIFLAZZ_USERNAME=your-username
DIGIFLAZZ_API_KEY=your-api-key
MIDTRANS_SERVER_KEY=your-server-key
MIDTRANS_CLIENT_KEY=your-client-key

# Redis (Optional)
REDIS_URL=redis://localhost:6379/0
```

## Deployment ke Railway

### Metode 1: Deploy via GitHub
1. **Connect Repository**
   ```bash
   # Push code ke GitHub repository
   git add .
   git commit -m "Prepare for Railway deployment"
   git push origin main
   ```

2. **Deploy di Railway**
   - Buka [Railway.app](https://railway.app)
   - Login dengan GitHub
   - Klik "New Project" → "Deploy from GitHub repo"
   - Pilih repository ini
   - Railway akan otomatis detect dan deploy

3. **Add Database**
   - Di dashboard Railway, klik "New" → "Database" → "PostgreSQL"
   - Database URL akan otomatis tersedia sebagai `${{ Postgres.DATABASE_URL }}`

### Metode 2: Deploy via Railway CLI
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy
railway up
```

## Troubleshooting

### Error: "Service Unavailable"
**Penyebab Umum:**
1. **Port Configuration**: Pastikan aplikasi listen di `0.0.0.0:$PORT`
2. **Dependencies**: Cek requirements.txt tidak ada duplikat
3. **Environment Variables**: Pastikan semua env vars sudah diset

**Solusi:**
```bash
# Cek logs
railway logs

# Restart service
railway service restart
```

### Error: "Exit Code 127" (pip install failed)
**Penyebab:**
- Nixpacks configuration tidak lengkap
- Missing system dependencies

**Solusi:**
File `nixpacks.toml` sudah dikonfigurasi dengan:
```toml
[phases.setup]
nixPkgs = ["python39", "pip", "gcc", "pkg-config"]

[phases.install]
cmds = ["pip install -r requirements.txt"]

[phases.build]
cmds = ["python -m compileall ."]

[start]
cmd = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
```

### Error: Database Connection
**Solusi:**
1. Pastikan PostgreSQL service sudah running di Railway
2. Cek DATABASE_URL environment variable
3. Test koneksi database:
```python
# Test di Railway console
python -c "from app.core.database import engine; print('DB OK')"
```

### Error: Import Module
**Penyebab:**
- Missing dependencies
- Python path issues

**Solusi:**
```bash
# Cek installed packages
pip list

# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

## Checklist Deployment

### Pre-Deployment ✅
- [ ] Code sudah di-commit dan push ke repository
- [ ] Requirements.txt sudah update dan tidak ada duplikat
- [ ] Environment variables sudah disiapkan
- [ ] Database migration scripts sudah siap
- [ ] Static files sudah dikonfigurasi

### Deployment Process ✅
- [ ] Railway project sudah dibuat
- [ ] Repository sudah connected
- [ ] PostgreSQL database sudah ditambahkan
- [ ] Environment variables sudah diset
- [ ] Domain sudah dikonfigurasi (optional)

### Post-Deployment ✅
- [ ] Health check endpoint berfungsi (`/health`)
- [ ] Database connection berhasil
- [ ] API endpoints dapat diakses
- [ ] Admin dashboard dapat diakses
- [ ] Logs tidak menunjukkan error critical

### Testing Checklist ✅
```bash
# Test health endpoint
curl https://your-app.railway.app/health

# Test API endpoint
curl https://your-app.railway.app/api/v1/health

# Test admin dashboard
curl https://your-app.railway.app/admin/
```

## Monitoring dan Maintenance

### Logs Monitoring
```bash
# Real-time logs
railway logs --follow

# Filter logs
railway logs --filter "ERROR"
```

### Performance Monitoring
- Monitor CPU dan Memory usage di Railway dashboard
- Set up alerts untuk downtime
- Regular health checks

### Database Maintenance
```bash
# Backup database
railway run python -c "from app.database.backup import backup_db; backup_db()"

# Run migrations
railway run alembic upgrade head
```

## Tips Optimasi

### Performance
1. **Enable Caching**: Redis sudah dikonfigurasi
2. **Database Indexing**: Pastikan index sudah optimal
3. **Static Files**: Gunakan CDN untuk static assets

### Security
1. **Environment Variables**: Jangan hardcode secrets
2. **HTTPS**: Railway menyediakan SSL otomatis
3. **Rate Limiting**: Sudah dikonfigurasi di aplikasi

### Cost Optimization
1. **Resource Monitoring**: Monitor usage di dashboard
2. **Database Optimization**: Optimize queries
3. **Caching Strategy**: Implement proper caching

## Support dan Resources

### Railway Documentation
- [Railway Docs](https://docs.railway.app/)
- [Python Deployment Guide](https://docs.railway.app/deploy/python)

### Project Resources
- Repository: [GitHub Repository]
- Documentation: `/docs` folder
- API Documentation: `/docs` endpoint (Swagger UI)

### Contact
Jika ada masalah deployment, cek:
1. Railway logs untuk error details
2. GitHub Issues untuk known problems
3. Documentation di `/docs` folder
