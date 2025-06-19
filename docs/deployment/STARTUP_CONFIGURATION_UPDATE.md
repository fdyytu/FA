# 🔄 Update Konfigurasi Startup Railway

## Perubahan yang Dilakukan

### ❌ Konfigurasi Lama (Tidak Valid)
```bash
# File yang menggunakan run.py (tidak ada)
Procfile: web: python run.py
Dockerfile: CMD ["python", "run.py"]
railway.json: "startCommand": "python run.py"
```

### ✅ Konfigurasi Baru (Valid)
```bash
# File yang menggunakan main.py (entry point sebenarnya)
Procfile: web: python main.py
Dockerfile: CMD ["python", "main.py"]
railway.json: "startCommand": "python main.py"
```

## Entry Point Aplikasi

### main.py
```python
"""
Entry point utama untuk FA Application
Menggunakan factory pattern dari app/main.py
"""
from app.main import app

if __name__ == "__main__":
    import uvicorn
    import os
    
    # Gunakan PORT dari environment variable atau default 8000
    port = int(os.environ.get("PORT", 8000))
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        reload=False
    )
```

## Opsi Deployment Railway

### 1. Procfile (Heroku-style)
```bash
# deployment/Procfile
web: python main.py
```
- Sederhana dan mudah dipahami
- Menggunakan main.py sebagai entry point
- Railway otomatis set PORT environment variable

### 2. Nixpacks (Direct uvicorn)
```toml
# config/nixpacks.toml
[start]
cmd = "uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1"
```
- Langsung menggunakan uvicorn
- Lebih kontrol terhadap konfigurasi server
- Mendukung multiple workers

### 3. Dockerfile (Containerized)
```dockerfile
# deployment/Dockerfile
CMD ["python", "main.py"]
```
- Full control terhadap environment
- Konsisten di semua platform
- Mendukung custom system dependencies

## Keuntungan Konfigurasi Baru

### ✅ Konsistensi
- Semua file deployment menggunakan entry point yang sama
- Tidak ada konflik antara konfigurasi yang berbeda

### ✅ Fleksibilitas
- main.py menangani PORT configuration otomatis
- Fallback ke port 8000 untuk development
- Host 0.0.0.0 untuk akses eksternal

### ✅ Maintainability
- Satu entry point untuk semua deployment method
- Mudah di-debug dan di-maintain
- Dokumentasi yang konsisten

## Testing Deployment

### Local Testing
```bash
# Test dengan PORT environment variable
PORT=3000 python main.py

# Test tanpa PORT (fallback ke 8000)
python main.py
```

### Railway Testing
```bash
# Deploy dan cek logs
railway logs --follow

# Test health endpoint
curl https://your-app.railway.app/health
```

## File yang Diperbarui

### 1. deployment/Procfile
```diff
- web: python run.py
+ web: python main.py
```

### 2. deployment/Dockerfile
```diff
- CMD ["python", "run.py"]
+ CMD ["python", "main.py"]
```

### 3. config/railway.json
```diff
- "startCommand": "python run.py",
+ "startCommand": "python main.py",
```

### 4. Dokumentasi
- ✅ `DEPLOYMENT_GUIDE_UNIFIED.md` - Updated startup commands
- ✅ `RINGKASAN_KONFIGURASI_RAILWAY.md` - Updated configuration summary
- ✅ `STARTUP_CONFIGURATION_UPDATE.md` - New documentation (this file)

## Troubleshooting

### Error: "python: can't open file 'run.py'"
**Solusi**: File sudah diperbarui ke `main.py`

### Error: "ModuleNotFoundError: No module named 'app'"
**Solusi**: Pastikan PYTHONPATH="/app" di environment variables

### Error: "Port already in use"
**Solusi**: Railway otomatis assign PORT, tidak perlu manual configuration

---
**Update dilakukan pada**: {current_date}
**Status**: ✅ Semua file deployment sudah diperbarui
