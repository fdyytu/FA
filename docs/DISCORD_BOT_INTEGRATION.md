# Discord Bot Integration untuk Growtopia Live Stock

## Overview

Sistem Discord Bot terintegrasi untuk mengelola Live Stock Growtopia dengan fitur:

- **Discord Bot Management**: Kelola multiple Discord bots
- **Live Stock System**: Real-time product management
- **User Wallet System**: Multi-currency wallet (WL/DL/BGL)
- **Admin Dashboard**: Web interface untuk management
- **Slash Commands**: Modern Discord interactions

## Fitur Utama

### 🤖 Discord Bot Features
- **Slash Commands**: `/buy`, `/growid`, `/balance`, `/world`
- **Interactive Buttons**: Quick actions pada live stock display
- **Modal Forms**: User-friendly input forms
- **Auto-refresh**: Live stock update setiap 5 menit
- **Multi-guild Support**: Satu bot untuk multiple servers

### 💰 Wallet System
- **Multi-currency**: World Lock (WL), Diamond Lock (DL), Blue Gem Lock (BGL)
- **Auto-conversion**: Konversi otomatis antar currency
- **Transaction History**: Tracking semua transaksi
- **Balance Management**: Admin dapat manage user balance

### 📦 Live Stock Management
- **Real-time Updates**: Stock update otomatis
- **Product Categories**: Organisasi produk berdasarkan kategori
- **Featured Products**: Highlight produk tertentu
- **Stock Alerts**: Notifikasi ketika stock habis

### 🎛️ Admin Dashboard
- **Bot Management**: Start/stop bots, konfigurasi
- **Product Management**: CRUD operations untuk live stock
- **User Management**: Monitor Discord users dan wallets
- **World Configuration**: Setup world admin
- **Statistics**: Dashboard analytics

## Struktur Database

### Discord Models
```sql
-- Discord Bots
discord_bots (id, bot_name, bot_token, guild_id, status, ...)

-- Discord Users
discord_users (id, discord_id, discord_username, grow_id, ...)

-- Discord Wallets
discord_wallets (id, user_id, wl_balance, dl_balance, bgl_balance, ...)

-- Live Stock Products
live_stocks (id, bot_id, product_code, product_name, price_wl, stock_quantity, ...)

-- Transactions
discord_transactions (id, user_id, transaction_type, currency_type, amount, ...)

-- World Configurations
admin_world_configs (id, world_name, world_description, access_level, ...)
```

## API Endpoints

### Discord Bot Management
```
POST   /api/v1/discord/bots              # Create bot
GET    /api/v1/discord/bots              # List bots
GET    /api/v1/discord/bots/{id}         # Get bot details
PUT    /api/v1/discord/bots/{id}         # Update bot
POST   /api/v1/discord/bots/{id}/start   # Start bot
POST   /api/v1/discord/bots/{id}/stop    # Stop bot
```

### Live Stock Management
```
POST   /api/v1/discord/live-stocks       # Add product
GET    /api/v1/discord/live-stocks       # List products
PUT    /api/v1/discord/live-stocks/{id}  # Update product
DELETE /api/v1/discord/live-stocks/{id}  # Delete product
```

### User & Wallet Management
```
GET    /api/v1/discord/discord-users     # List Discord users
GET    /api/v1/discord/stats             # Get statistics
```

### World Configuration
```
POST   /api/v1/discord/world-configs     # Add world config
GET    /api/v1/discord/world-configs     # List world configs
PUT    /api/v1/discord/world-configs/{id} # Update world config
```

## Discord Commands

### Slash Commands

#### `/buy <product_code> <quantity> [currency]`
Membeli produk dari live stock
- `product_code`: Kode produk (required)
- `quantity`: Jumlah yang dibeli (required)
- `currency`: WL/DL/BGL (optional, default: WL)

#### `/growid [grow_id]`
Set atau lihat Grow ID
- `grow_id`: Grow ID untuk disimpan (optional)

#### `/balance`
Lihat saldo wallet (WL/DL/BGL)

#### `/world`
Lihat daftar world admin yang tersedia

### Interactive Components

#### Live Stock Display
- **Auto-refresh**: Update setiap 5 menit
- **Product Cards**: Menampilkan nama, kode, harga, stock
- **Status Indicators**: Available/Out of Stock
- **Featured Badge**: Highlight produk unggulan

#### Action Buttons
- **🛒 Buy**: Buka modal pembelian
- **🌱 Grow ID**: Set Grow ID
- **💰 Balance**: Lihat saldo
- **🌍 World**: Lihat world list

## Setup & Configuration

### 1. Environment Variables
```env
# Discord Bot Configuration
DISCORD_BOT_TOKEN=your_bot_token_here
DISCORD_GUILD_ID=your_guild_id_here
DISCORD_LIVE_STOCK_CHANNEL_ID=your_channel_id_here

# Database
DATABASE_URL=postgresql://user:password@localhost/dbname
```

### 2. Database Migration
```bash
# Run Discord models migration
alembic upgrade head
```

### 3. Discord Bot Setup
1. Create Discord Application di Discord Developer Portal
2. Create Bot dan copy token
3. Enable necessary intents:
   - Message Content Intent
   - Server Members Intent
4. Invite bot ke server dengan permissions:
   - Send Messages
   - Use Slash Commands
   - Embed Links
   - Read Message History

### 4. Admin Dashboard Access
```
GET /api/v1/admin/discord-dashboard
```
Requires admin authentication.

## Usage Examples

### 1. Setup Discord Bot
```python
# Via API
POST /api/v1/discord/bots
{
    "bot_name": "Growtopia Live Stock Bot",
    "bot_token": "your_bot_token",
    "guild_id": "123456789",
    "live_stock_channel_id": "987654321"
}
```

### 2. Add Live Stock Product
```python
# Via API
POST /api/v1/discord/live-stocks
{
    "bot_id": 1,
    "product_code": "DIRT",
    "product_name": "Dirt Seed",
    "price_wl": 1.5,
    "stock_quantity": 100,
    "category": "Seeds",
    "is_featured": true
}
```

### 3. Discord User Interaction
```
User: /buy DIRT 10 WL
Bot: ✅ Pembelian Berhasil
     Berhasil membeli 10x Dirt Seed
     Saldo Tersisa: WL: 85.0, DL: 0, BGL: 0
```

## Security Features

### 1. Authentication
- Admin-only access untuk management endpoints
- User verification system untuk Discord users
- Secure token storage

### 2. Data Protection
- Encrypted bot tokens
- Input validation dan sanitization
- Rate limiting pada API endpoints

### 3. Transaction Security
- Atomic transactions untuk wallet operations
- Transaction logging dan audit trail
- Balance validation sebelum transaksi

## Monitoring & Logging

### 1. Bot Status Monitoring
- Real-time bot status tracking
- Connection health checks
- Error logging dan alerting

### 2. Transaction Monitoring
- Real-time transaction tracking
- Fraud detection patterns
- Balance anomaly detection

### 3. Performance Metrics
- Command response times
- API endpoint performance
- Database query optimization

## Troubleshooting

### Common Issues

#### Bot Not Responding
1. Check bot status di admin dashboard
2. Verify bot token dan permissions
3. Check Discord API rate limits

#### Commands Not Working
1. Ensure slash commands are synced
2. Check bot permissions di Discord server
3. Verify guild ID configuration

#### Database Errors
1. Check database connection
2. Run pending migrations
3. Verify table permissions

### Error Codes
- `400`: Bad Request - Invalid input data
- `401`: Unauthorized - Authentication required
- `403`: Forbidden - Insufficient permissions
- `404`: Not Found - Resource not found
- `500`: Internal Server Error - Server error

## Development

### Adding New Commands
1. Define command di `DiscordBotService._setup_commands()`
2. Implement handler method
3. Add corresponding API endpoint jika diperlukan
4. Update documentation

### Adding New Features
1. Update database models jika diperlukan
2. Create migration file
3. Implement service layer
4. Add API endpoints
5. Update admin dashboard
6. Write tests

## Contributing

1. Fork repository
2. Create feature branch
3. Implement changes dengan tests
4. Submit pull request
5. Code review process

## License

MIT License - see LICENSE file for details.
