# Setup Discord Bot

Script ini digunakan untuk menambahkan konfigurasi Discord Bot ke dalam aplikasi FA.

## Prasyarat

1. **Discord Bot Token**: Dapatkan dari Discord Developer Portal
2. **Discord Admin ID**: ID pengguna Discord yang akan menjadi admin bot
3. **Environment Variables**: Konfigurasi di file `.env`

## Konfigurasi Environment Variables

Tambahkan konfigurasi berikut ke file `.env`:

```env
# Discord Bot Configuration
DISCORD_TOKEN=your_discord_bot_token_here
DISCORD_COMMAND_PREFIX=!
DISCORD_ADMIN_ID=your_discord_admin_user_id
DISCORD_GUILD_ID=
DISCORD_BOT_ENABLED=True
```

## Cara Penggunaan

1. **Setup Database** (jika belum):
   ```bash
   python3 scripts/database/auto_create_tables.py
   ```

2. **Jalankan Setup Discord Bot**:
   ```bash
   python3 scripts/setup_discord_bot.py
   ```

3. **Jalankan Aplikasi**:
   ```bash
   python3 main.py
   ```

4. **Test Bot Status**:
   ```bash
   curl http://localhost:8000/api/v1/discord/bot/status
   ```

## Fitur yang Dikonfigurasi

- ✅ **Discord Bot Configuration**: Token dan pengaturan bot
- ✅ **Admin Account**: Akun admin untuk dashboard
- ✅ **Discord Admin ID**: ID admin untuk manajemen bot
- ✅ **Database Tables**: Semua tabel yang diperlukan

## Akses Dashboard

Setelah setup berhasil, Anda dapat mengakses:

- **API Documentation**: `/docs`
- **Admin Login**: `/api/v1/admin/auth/login`
- **Discord Dashboard**: `/api/v1/admin/discord/`

## Kredensial Default Admin

- **Username**: `admin`
- **Password**: `admin123`
- **Role**: `SUPER_ADMIN`

⚠️ **Penting**: Ganti password default setelah login pertama!

## Troubleshooting

### Error: DISCORD_TOKEN tidak ditemukan
- Pastikan file `.env` ada di root project
- Pastikan `DISCORD_TOKEN` sudah dikonfigurasi dengan benar

### Error: Database connection
- Jalankan script `auto_create_tables.py` terlebih dahulu
- Pastikan `DATABASE_URL` dikonfigurasi dengan benar

### Bot tidak terhubung
- Pastikan token Discord valid
- Pastikan bot sudah diundang ke server Discord
- Periksa permissions bot di Discord server
