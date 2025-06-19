# FA - FastAPI Application

Aplikasi FastAPI dengan arsitektur Domain-Driven Design (DDD) yang telah direstrukturisasi untuk kemudahan maintenance dan pengembangan.

## Struktur Proyek

```
/
├── app/                    # Aplikasi utama
│   ├── api/               # API routes dan endpoints
│   │   └── v1/           # API versi 1
│   ├── cache/            # Sistem caching
│   ├── core/             # Konfigurasi inti aplikasi
│   ├── domains/          # Domain logic (DDD)
│   │   ├── admin/        # Domain admin
│   │   ├── auth/         # Domain authentication
│   │   ├── ppob/         # Domain PPOB
│   │   ├── wallet/       # Domain wallet
│   │   └── ...           # Domain lainnya
│   ├── infrastructure/   # Integrasi eksternal
│   ├── middleware/       # Middleware aplikasi
│   ├── models/           # Base models
│   ├── shared/           # Utilities bersama
│   └── utils/            # Helper utilities
├── docs/                 # Dokumentasi
├── tests/                # Test files
├── alembic/              # Database migrations
├── static/               # Static files
├── requirements.txt      # Dependencies
└── main.py              # Entry point aplikasi
```

## Fitur Utama

- **Authentication & Authorization**: Sistem login dan manajemen user
- **PPOB (Payment Point Online Bank)**: Layanan pembayaran online
- **Wallet Management**: Manajemen dompet digital
- **Admin Dashboard**: Panel administrasi
- **Notification System**: Sistem notifikasi
- **File Monitoring**: Monitoring file system
- **Caching System**: Sistem cache untuk performa
- **Discord Integration**: Integrasi dengan Discord bot

## Instalasi

1. Clone repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Setup environment variables (copy dari .env.example)
4. Jalankan migrasi database:
   ```bash
   alembic upgrade head
   ```
5. Jalankan aplikasi:
   ```bash
   python main.py
   ```

## Pengembangan

Aplikasi ini menggunakan arsitektur Domain-Driven Design (DDD) dengan struktur:

- **Controllers**: Menangani HTTP requests
- **Services**: Business logic
- **Repositories**: Data access layer
- **Models**: Database models
- **Schemas**: Request/Response schemas

## API Documentation

Setelah aplikasi berjalan, akses dokumentasi API di:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Deployment

### Railway Deployment
Aplikasi sudah dikonfigurasi untuk deployment di Railway:

1. **File Konfigurasi**:
   - `deployment/Procfile` - Heroku-style startup
   - `config/nixpacks.toml` - Nixpacks build configuration
   - `config/railway.json` - Railway deployment settings
   - `deployment/Dockerfile` - Container deployment

2. **Deploy ke Railway**:
   ```bash
   # Via Railway CLI
   railway login
   railway up
   
   # Atau connect via GitHub di railway.app
   ```

3. **Environment Variables**:
   - Copy dari `config/.env.railway.example`
   - Set di Railway dashboard atau via CLI

4. **Database**:
   - Tambah PostgreSQL service di Railway
   - DATABASE_URL otomatis tersedia

Lihat dokumentasi lengkap di `docs/deployment/`

## Testing

Jalankan tests dengan:
```bash
pytest tests/
```

## Kontribusi

1. Fork repository
2. Buat feature branch
3. Commit perubahan
4. Push ke branch
5. Buat Pull Request
