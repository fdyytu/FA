# Analisis File Controller yang Terduplikat

## File Controller yang Terduplikat Ditemukan:

### 1. auth_controller.py
- **Lokasi 1**: `/app/domains/admin/controllers/auth_controller.py` (80 lines)
  - **Fungsi**: Admin authentication (login/logout admin)
  - **Endpoint**: `/login`, `/logout`
  - **Digunakan untuk**: Autentikasi admin

- **Lokasi 2**: `/app/domains/auth/controllers/auth_controller.py` (335 lines)
  - **Fungsi**: User authentication (login/logout user)
  - **Endpoint**: `/login`, `/refresh`, `/me`, `/change-password`, `/stats`
  - **Digunakan untuk**: Autentikasi user biasa

**Status**: TIDAK TERDUPLIKAT - Fungsi berbeda (admin vs user)

### 2. analytics_controller.py
- **Lokasi 1**: `/app/domains/analytics/controllers/analytics_controller.py` (1452 lines)
  - **Fungsi**: Analytics umum untuk aplikasi
  - **Endpoint**: `/events`, `/dashboard`, `/overview`, `/revenue`, `/orders`
  - **Digunakan untuk**: Analytics aplikasi secara umum

- **Lokasi 2**: `/app/domains/discord/controllers/analytics_controller.py` (318 lines)
  - **Fungsi**: Analytics khusus Discord
  - **Endpoint**: `/logs`, `/commands/recent`, `/stats`, `/stats/commands`, `/stats/performance`
  - **Digunakan untuk**: Analytics Discord bot

**Status**: TIDAK TERDUPLIKAT - Fungsi berbeda (general vs discord analytics)

### 3. user_controller.py
- **Lokasi 1**: `/app/domains/user/controllers/user_controller.py` (266 lines)
  - **Fungsi**: Manajemen user untuk admin dashboard
  - **Endpoint**: `/stats`, `/`, `/`, `/{user_id}`, `/{user_id}/status`, `/{user_id}/balance`
  - **Digunakan untuk**: Admin mengelola user

- **Lokasi 2**: `/app/domains/discord/controllers/user_controller.py` (295 lines)
  - **Fungsi**: Manajemen Discord user
  - **Endpoint**: `/`, `/{user_id}`, `/{user_id}/verify`, `/{user_id}/wallet`, `/{user_id}/wallet/balance`, `/stats/summary`
  - **Digunakan untuk**: Mengelola Discord user dan wallet

**Status**: TIDAK TERDUPLIKAT - Fungsi berbeda (general user vs discord user)

### 4. product_controller.py
- **Lokasi 1**: `/app/domains/product/controllers/product_controller.py` (379 lines)
  - **Fungsi**: Manajemen produk umum
  - **Endpoint**: `/`, `/{product_id}`, `/search`, `/category/{category}`, `/code/{code}`, `/{product_id}/toggle-status`, `/stats`
  - **Digunakan untuk**: CRUD produk umum

- **Lokasi 2**: `/app/domains/discord/controllers/product_controller.py` (380 lines)
  - **Fungsi**: Manajemen produk Discord (LiveStock & World Config)
  - **Endpoint**: `/livestocks`, `/livestocks/{livestock_id}`, `/worlds`, `/worlds/{world_id}`
  - **Digunakan untuk**: Mengelola LiveStock dan World Configuration Discord

**Status**: TIDAK TERDUPLIKAT - Fungsi berbeda (general product vs discord product)

### 5. transaction_controller.py
- **Lokasi 1**: `/app/domains/admin/controllers/transaction_controller.py` (262 lines)
  - **Fungsi**: Manajemen transaksi untuk admin dengan audit log
  - **Endpoint**: `/recent`, `/`, `/{transaction_id}`, `/{transaction_id}/status`, `/stats/summary`
  - **Digunakan untuk**: Admin mengelola transaksi dengan audit

- **Lokasi 2**: `/app/domains/transaction/controllers/transaction_controller.py` (191 lines)
  - **Fungsi**: Manajemen transaksi sederhana
  - **Endpoint**: `/recent`, `/`, `/stats`
  - **Digunakan untuk**: Endpoint transaksi dasar

**Status**: TERDUPLIKAT SEBAGIAN - Ada overlap fungsi

## Analisis Penggunaan di Dashboard:

### Dashboard Endpoints yang Digunakan:
1. **Dashboard Main** (`dashboard_main.js`):
   - `/admin/stats` - untuk statistik umum
   - `/admin/transactions/transactions/recent?limit=5` - untuk transaksi terbaru

2. **Discord Dashboard** (`discord_handlers.js`):
   - `/discord/logs?limit=10` - untuk log Discord
   - `/discord/commands/recent?limit=5` - untuk command terbaru
   - `/discord/bots` - untuk daftar bot

3. **Discord Management** (`dashboard_discord.js`):
   - `/admin/discord/stats` - untuk statistik Discord
   - `/admin/discord/bots` - untuk manajemen bot
   - `/admin/discord/bots/{botId}/{action}` - untuk start/stop bot
   - `/admin/discord/bots/{botId}` - untuk delete bot
   - `/admin/discord/worlds` - untuk manajemen world
   - `/admin/discord/worlds/{worldId}` - untuk delete world
   - `/admin/discord/logs` - untuk clear logs

## Kesimpulan:

**File yang BENAR-BENAR TERDUPLIKAT dan perlu dihapus:**
- `/app/domains/transaction/controllers/transaction_controller.py` - karena fungsinya sudah ada di admin/controllers/transaction_controller.py yang lebih lengkap

**File yang TIDAK TERDUPLIKAT (berbeda fungsi):**
- Semua file lainnya memiliki fungsi yang berbeda dan spesifik untuk domain masing-masing

**Rekomendasi:**
1. Hapus `/app/domains/transaction/controllers/transaction_controller.py`
2. Pastikan routing menggunakan admin/controllers/transaction_controller.py
3. Semua file controller lainnya tetap dipertahankan karena memiliki fungsi yang berbeda
