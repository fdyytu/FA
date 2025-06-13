# ✅ Checklist Deployment Railway

## 📋 Persiapan Sebelum Deploy

### 1. File Konfigurasi (✅ Sudah Siap)
- [x] `railway.json` - Konfigurasi Railway
- [x] `Procfile` - Command startup
- [x] `requirements.txt` - Dependencies Python
- [x] `runtime.txt` - Python version (3.11.0)

### 2. Environment Variables
- [ ] Generate SECRET_KEY dengan menjalankan: `python3 generate_secret_key.py`
- [ ] Siapkan credentials external services (Digiflazz, Midtrans, dll)
- [ ] Catat semua environment variables yang diperlukan

## 🚀 Langkah Deployment

### Step 1: Setup Railway Account
- [ ] Buka https://railway.app
- [ ] Login dengan GitHub account
- [ ] Authorize Railway untuk akses repository

### Step 2: Create New Project
- [ ] Klik "New Project"
- [ ] Pilih "Deploy from GitHub repo"
- [ ] Pilih repository "FA"
- [ ] Tunggu Railway detect sebagai Python app

### Step 3: Add PostgreSQL Database
- [ ] Di project dashboard, klik "+ New"
- [ ] Pilih "Database" → "Add PostgreSQL"
- [ ] Tunggu database provisioning selesai
- [ ] Verify `DATABASE_URL` ter-set otomatis

### Step 4: Set Environment Variables
Copy dari hasil `generate_secret_key.py`:
- [ ] `SECRET_KEY=<generated-key>`
- [ ] `ADMIN_PASSWORD=<generated-password>`
- [ ] `ALGORITHM=HS256`
- [ ] `ACCESS_TOKEN_EXPIRE_MINUTES=30`
- [ ] `DEBUG=False`
- [ ] `ENVIRONMENT=production`

Optional (jika diperlukan):
- [ ] `DIGIFLAZZ_USERNAME=<your-username>`
- [ ] `DIGIFLAZZ_API_KEY=<your-api-key>`
- [ ] `MIDTRANS_SERVER_KEY=<your-server-key>`
- [ ] `MIDTRANS_CLIENT_KEY=<your-client-key>`

### Step 5: Deploy Application
- [ ] Klik "Deploy" atau push ke GitHub
- [ ] Monitor deployment logs
- [ ] Tunggu status "Success"

### Step 6: Generate Public Domain
- [ ] Buka "Settings" tab
- [ ] Scroll ke "Domains" section
- [ ] Klik "Generate Domain"
- [ ] Catat URL: `https://your-app.up.railway.app`

## 🧪 Testing Deployment

### Health Check
- [ ] Akses: `https://your-app.up.railway.app/health`
- [ ] Harus return status 200 OK

### API Documentation
- [ ] Akses: `https://your-app.up.railway.app/docs`
- [ ] Verify Swagger UI terbuka dengan benar

### Database Connection
- [ ] Check logs untuk konfirmasi database connection
- [ ] Verify tables ter-create dengan benar

### Admin Access
- [ ] Akses admin dashboard (jika ada)
- [ ] Test login dengan ADMIN_USERNAME dan ADMIN_PASSWORD

## 🔧 Post-Deployment

### Monitoring
- [ ] Setup monitoring di Railway dashboard
- [ ] Check resource usage (CPU, Memory)
- [ ] Monitor application logs

### Security
- [ ] Verify HTTPS enabled (otomatis)
- [ ] Check CORS settings
- [ ] Validate environment variables tidak ter-expose

### Performance
- [ ] Test API response time
- [ ] Check database query performance
- [ ] Monitor error rates

## 🐛 Troubleshooting Common Issues

### Build Failed
- [ ] Check Python version di `runtime.txt`
- [ ] Verify `requirements.txt` syntax
- [ ] Check for import errors di logs

### Database Connection Error
- [ ] Verify PostgreSQL service running
- [ ] Check `DATABASE_URL` format
- [ ] Confirm database tables created

### Application Won't Start
- [ ] Check startup command di `Procfile`
- [ ] Verify port binding (`$PORT` environment variable)
- [ ] Check application logs for errors

### 502 Bad Gateway
- [ ] Confirm app binding to `0.0.0.0:$PORT`
- [ ] Check health endpoint response
- [ ] Verify no blocking operations di startup

## 📊 Success Metrics

### Deployment Success
- [ ] Build completed without errors
- [ ] Application starts successfully
- [ ] Health check returns 200
- [ ] API docs accessible

### Functionality
- [ ] Database operations working
- [ ] Authentication working
- [ ] External API integrations working
- [ ] Admin functions accessible

### Performance
- [ ] Response time < 2 seconds
- [ ] Memory usage < 512MB
- [ ] No critical errors di logs

## 🎉 Deployment Complete!

Jika semua checklist di atas sudah ✅, maka deployment Anda berhasil!

**URL Aplikasi**: `https://your-app.up.railway.app`
**API Docs**: `https://your-app.up.railway.app/docs`
**Admin Panel**: `https://your-app.up.railway.app/static/admin/login.html`

## 📞 Support

Jika ada masalah:
1. Check Railway deployment logs
2. Lihat troubleshooting guide di `PANDUAN_DEPLOY_RAILWAY.md`
3. Konsultasi Railway documentation
4. Join Railway Discord community

---
*Checklist ini dibuat untuk memastikan deployment Railway berjalan lancar.*
