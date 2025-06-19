# Discord API Structure Documentation

## Overview
Struktur API Discord telah diperbaiki dan diorganisir berdasarkan Single Responsibility Principle dengan pemisahan yang jelas antara domain controllers dan API endpoints.

## API Structure

### 1. Domain Controllers (`/discord/`)
Domain controllers mengelola logika bisnis dan operasi internal Discord bot.

#### Discord Bot Controller (`/discord/bot/`)
- **POST** `/discord/bot/config` - Buat konfigurasi Discord Bot baru
- **GET** `/discord/bot/config` - Ambil daftar Discord Bot
- **GET** `/discord/bot/config/{bot_id}` - Ambil detail Discord Bot
- **PUT** `/discord/bot/config/{bot_id}` - Update Discord Bot
- **DELETE** `/discord/bot/config/{bot_id}` - Hapus Discord Bot
- **POST** `/discord/bot/operations/{bot_id}/start` - Start Discord Bot
- **POST** `/discord/bot/operations/{bot_id}/stop` - Stop Discord Bot
- **GET** `/discord/bot/operations/{bot_id}/status` - Ambil status Discord Bot

#### Discord Analytics Controller (`/discord/analytics/`)
- **GET** `/discord/analytics/logs` - Ambil log Discord Bot
- **GET** `/discord/analytics/commands/recent` - Ambil recent commands
- **GET** `/discord/analytics/commands` - Ambil Discord commands dengan filter
- **GET** `/discord/analytics/stats` - Ambil statistik Discord Bot
- **GET** `/discord/analytics/performance` - Ambil performance metrics
- **GET** `/discord/analytics/errors` - Ambil error logs

#### Discord User Controller (`/discord/users/`)
- **GET** `/discord/users/` - Ambil daftar Discord User
- **GET** `/discord/users/{user_id}` - Ambil detail Discord User
- **PUT** `/discord/users/{user_id}/verify` - Verifikasi Discord User
- **GET** `/discord/users/{user_id}/wallet` - Ambil wallet Discord User
- **POST** `/discord/users/{user_id}/wallet/topup` - Top up wallet
- **POST** `/discord/users/{user_id}/wallet/withdraw` - Withdraw dari wallet
- **GET** `/discord/users/{user_id}/transactions` - Ambil riwayat transaksi

#### Discord Product Controller (`/discord/products/`)
- **GET** `/discord/products/livestocks` - Ambil daftar LiveStock
- **POST** `/discord/products/livestocks` - Buat LiveStock baru
- **GET** `/discord/products/livestocks/{livestock_id}` - Ambil detail LiveStock
- **PUT** `/discord/products/livestocks/{livestock_id}` - Update LiveStock
- **DELETE** `/discord/products/livestocks/{livestock_id}` - Hapus LiveStock
- **GET** `/discord/products/world-configs` - Ambil konfigurasi world
- **POST** `/discord/products/world-configs` - Buat konfigurasi world baru
- **GET** `/discord/products/world-configs/{config_id}` - Ambil detail konfigurasi world
- **PUT** `/discord/products/world-configs/{config_id}` - Update konfigurasi world
- **DELETE** `/discord/products/world-configs/{config_id}` - Hapus konfigurasi world

#### Discord Config Controller (`/discord/config/`)
- **POST** `/discord/config/` - Buat konfigurasi Discord baru
- **GET** `/discord/config/` - Ambil semua konfigurasi Discord
- **GET** `/discord/config/active` - Ambil konfigurasi Discord yang aktif
- **GET** `/discord/config/{config_id}` - Ambil konfigurasi Discord berdasarkan ID
- **PUT** `/discord/config/{config_id}` - Update konfigurasi Discord
- **DELETE** `/discord/config/{config_id}` - Hapus konfigurasi Discord
- **POST** `/discord/config/{config_id}/activate` - Aktifkan konfigurasi Discord
- **POST** `/discord/config/test` - Test konfigurasi Discord

### 2. API Endpoints (`/api/discord/`)
API endpoints untuk manajemen Discord bot dari dashboard/frontend.

#### Discord Bot Management API (`/api/discord/bot/`)
- **GET** `/api/discord/bot/management/status` - Get Discord bot status
- **POST** `/api/discord/bot/management/start` - Start Discord bot
- **POST** `/api/discord/bot/management/stop` - Stop Discord bot
- **POST** `/api/discord/bot/management/restart` - Restart Discord bot
- **POST** `/api/discord/bot/management/send-message` - Send message to Discord channel
- **GET** `/api/discord/bot/management/health` - Check Discord bot health

#### Discord Config Management API (`/api/discord/config/`)
- **GET** `/api/discord/config/` - Get all Discord configurations
- **POST** `/api/discord/config/` - Create new Discord configuration
- **GET** `/api/discord/config/{config_id}` - Get Discord configuration by ID
- **PUT** `/api/discord/config/{config_id}` - Update Discord configuration
- **DELETE** `/api/discord/config/{config_id}` - Delete Discord configuration
- **POST** `/api/discord/config/{config_id}/activate` - Activate Discord configuration
- **POST** `/api/discord/config/test` - Test Discord configuration
- **GET** `/api/discord/config/active` - Get active Discord configuration

## Key Improvements

### 1. **Clear Separation of Concerns**
- **Domain Controllers**: Handle business logic and internal operations
- **API Endpoints**: Handle external API requests and dashboard integration

### 2. **Consistent URL Structure**
- Domain controllers use `/discord/{domain}/` pattern
- API endpoints use `/api/discord/{domain}/` pattern
- Clear prefixes for different types of operations (config, operations, management)

### 3. **Single Responsibility Principle**
- Each controller has a specific responsibility
- Bot Controller: Bot configuration and operations
- Analytics Controller: Logs, stats, and monitoring
- User Controller: User and wallet management
- Product Controller: LiveStock and world configuration
- Config Controller: Discord configuration management

### 4. **Proper Error Handling**
- All endpoints include proper try-catch blocks
- Consistent error response format
- Detailed logging for debugging

### 5. **Route Organization**
- Configuration routes: `/config/`
- Operational routes: `/operations/`
- Management routes: `/management/`

## Total Routes
- **Domain Controllers**: 39 routes
- **API Endpoints**: 14 routes
- **Total Discord Routes**: 53 routes

## Usage Examples

### Start Discord Bot
```bash
POST /api/discord/bot/management/start
```

### Get Bot Status
```bash
GET /api/discord/bot/management/status
```

### Create Bot Configuration
```bash
POST /discord/bot/config
{
  "name": "My Discord Bot",
  "guild_id": "123456789",
  "token": "bot_token_here"
}
```

### Get Analytics Stats
```bash
GET /discord/analytics/stats
```

### Manage User Wallet
```bash
POST /discord/users/{user_id}/wallet/topup
{
  "amount": 10000,
  "description": "Top up wallet"
}
```
