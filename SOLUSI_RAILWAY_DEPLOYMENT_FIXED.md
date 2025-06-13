# Solusi Masalah Railway Deployment - Exit Code 127

## Masalah yang Ditemukan
Error `exit code: 127` pada command `pip install -r requirements.txt` menunjukkan bahwa pip tidak ditemukan atau tidak dapat dieksekusi dengan benar.

## Penyebab Masalah
1. **Nixpacks Configuration**: Konfigurasi nixpacks.toml tidak menyertakan pip package secara eksplisit
2. **Missing Dependencies**: Beberapa system dependencies yang diperlukan untuk kompilasi package Python tidak tersedia
3. **Python Path Issues**: Environment variables tidak dikonfigurasi dengan benar

## Solusi yang Diterapkan

### 1. Perbaikan nixpacks.toml
```toml
[phases.setup]
nixPkgs = ["python311", "python311Packages.pip", "python311Packages.setuptools", "python311Packages.wheel", "postgresql", "gcc", "pkg-config"]

[phases.install]
cmds = [
  "python --version",
  "python -m pip --version", 
  "python -m pip install --upgrade pip setuptools wheel",
  "python -m pip install -r requirements.txt --no-cache-dir"
]

[phases.build]
cmds = ["echo 'Build completed'"]

[start]
cmd = "uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1"

[variables]
PYTHONPATH = "/app"
PYTHONUNBUFFERED = "1"
PIP_NO_CACHE_DIR = "1"
PIP_DISABLE_PIP_VERSION_CHECK = "1"
```

**Perubahan yang dilakukan:**
- Menambahkan `python311Packages.pip` secara eksplisit
- Menambahkan `setuptools` dan `wheel` untuk build dependencies
- Menambahkan `gcc` dan `pkg-config` untuk kompilasi native extensions
- Menggunakan `python -m pip` untuk memastikan pip yang benar digunakan
- Menambahkan `--no-cache-dir` untuk menghindari masalah cache
- Menambahkan version check commands untuk debugging

### 2. Alternatif Dockerfile
Dibuat Dockerfile sebagai backup jika nixpacks masih bermasalah:

```dockerfile
FROM python:3.11.7-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    pkg-config \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

EXPOSE $PORT

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1"]
```

### 3. Update railway.json
```json
{
  "build": {
    "builder": "DOCKERFILE"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### 4. Tambahan .dockerignore
Dibuat file .dockerignore untuk mengoptimalkan build process dan mengurangi ukuran image.

## Langkah Deployment

### Opsi 1: Menggunakan Dockerfile (Direkomendasikan)
1. Pastikan railway.json menggunakan `"builder": "DOCKERFILE"`
2. Commit dan push perubahan
3. Railway akan menggunakan Dockerfile untuk build

### Opsi 2: Menggunakan Nixpacks (Jika ingin tetap menggunakan nixpacks)
1. Ubah railway.json kembali ke `"builder": "NIXPACKS"`
2. Pastikan nixpacks.toml sudah diperbaiki
3. Commit dan push perubahan

## Verifikasi Deployment
1. Cek build logs di Railway dashboard
2. Pastikan semua dependencies terinstall dengan benar
3. Test endpoint `/health` untuk memastikan aplikasi berjalan
4. Monitor aplikasi setelah deployment

## Dependencies yang Diperlukan
- Python 3.11.7
- PostgreSQL (untuk database)
- GCC (untuk kompilasi native extensions)
- pkg-config (untuk konfigurasi package)
- libpq-dev (untuk psycopg2)

## Troubleshooting Tambahan
Jika masih ada masalah:
1. Cek Railway logs untuk error spesifik
2. Pastikan semua environment variables sudah diset
3. Verifikasi bahwa semua dependencies di requirements.txt kompatibel
4. Coba build lokal menggunakan Docker untuk testing

## Environment Variables yang Diperlukan
Pastikan environment variables berikut sudah diset di Railway:
- `DATABASE_URL` (untuk PostgreSQL)
- `SECRET_KEY` (untuk aplikasi)
- Environment variables lain sesuai kebutuhan aplikasi

Dengan perubahan ini, masalah exit code 127 seharusnya teratasi dan deployment ke Railway akan berhasil.
