# Callback System Documentation

## Overview

Sistem callback yang terorganisir untuk mengelola berbagai jenis callback dan webhook dari provider eksternal seperti payment gateway, PPOB provider, Discord bot, dan file system events.

## Struktur Direktori

```
app/callbacks/
├── __init__.py
├── base/
│   ├── __init__.py
│   └── base_handlers.py          # Base classes untuk callback handlers
├── payment/
│   ├── __init__.py
│   └── midtrans_callback.py      # Midtrans payment callbacks
├── ppob/
│   ├── __init__.py
│   └── ppob_callbacks.py         # PPOB provider callbacks (Digiflazz)
├── discord/
│   ├── __init__.py
│   └── discord_callbacks.py      # Discord bot event handlers
├── file_monitor/
│   ├── __init__.py
│   └── file_callbacks.py         # File system event handlers
├── notification/
│   ├── __init__.py
│   └── notification_callbacks.py # Notification webhook handlers
├── callback_manager.py           # Central callback manager
└── callback_controller.py        # FastAPI controller untuk endpoints
```

## Komponen Utama

### 1. Base Handlers (`base/base_handlers.py`)

Base classes yang menyediakan interface dan implementasi dasar:

- **BaseCallbackHandler**: Abstract base class untuk semua callback handlers
- **WebhookCallbackHandler**: Base class khusus untuk webhook callbacks
- **EventCallbackHandler**: Base class khusus untuk event callbacks
- **CallbackRegistry**: Registry untuk mengelola callback handlers

### 2. Payment Callbacks (`payment/midtrans_callback.py`)

Handler untuk payment gateway callbacks:

- **MidtransCallbackHandler**: Mengelola webhook dari Midtrans
  - Verifikasi notification
  - Update status transaksi
  - Update saldo wallet
  - Kirim notifikasi ke user

### 3. PPOB Callbacks (`ppob/ppob_callbacks.py`)

Handler untuk PPOB provider callbacks:

- **DigiflazzCallbackHandler**: Mengelola webhook dari Digiflazz
  - Update status transaksi PPOB
  - Kirim notifikasi ke user
- **PPOBCallbackFactory**: Factory untuk membuat PPOB handlers

### 4. Discord Callbacks (`discord/discord_callbacks.py`)

Handler untuk Discord bot events:

- **DiscordBotEventHandler**: Mengelola Discord bot events
  - on_ready, on_message, on_command_error
  - on_member_join, on_member_remove
- **DiscordSlashCommandHandler**: Mengelola slash commands

### 5. File Monitor Callbacks (`file_monitor/file_callbacks.py`)

Handler untuk file system events:

- **FileMonitorCallbackHandler**: Mengelola file system events
  - File created, modified, deleted
  - Process berdasarkan jenis file
- **FileUploadCallbackHandler**: Mengelola file upload events
  - Validasi file upload
  - Process berdasarkan upload type

### 6. Notification Callbacks (`notification/notification_callbacks.py`)

Handler untuk notification webhooks:

- **NotificationWebhookHandler**: Router untuk berbagai notification webhooks
- **DiscordWebhookHandler**: Kirim Discord webhooks
- **TelegramWebhookHandler**: Kirim Telegram messages
- **NotificationCallbackFactory**: Factory untuk notification handlers

### 7. Callback Manager (`callback_manager.py`)

Central manager untuk mengelola semua callback handlers:

- **CallbackManager**: Mengelola dan mengkoordinasikan handlers
- **CallbackRouter**: Router untuk mengarahkan callback ke handler yang tepat
- Global functions: `get_callback_manager()`, `initialize_callbacks()`

### 8. Callback Controller (`callback_controller.py`)

FastAPI controller untuk callback endpoints:

- Webhook endpoints: `/callbacks/webhook/{provider}`
- Event endpoints: `/callbacks/event/{type}`
- Management endpoints: `/callbacks/handlers`, `/callbacks/stats`

## Cara Penggunaan

### 1. Inisialisasi Callback System

```python
from app.callbacks.callback_manager import initialize_callbacks
from app.core.database import get_db

# Initialize callback system
db = next(get_db())
callback_manager = initialize_callbacks(db)
```

### 2. Register Custom Handler

```python
from app.callbacks.base.base_handlers import WebhookCallbackHandler

class CustomWebhookHandler(WebhookCallbackHandler):
    def __init__(self):
        super().__init__("CustomWebhook", "custom")
    
    async def handle(self, data):
        # Custom logic here
        return {"success": True, "message": "Custom webhook processed"}

# Register handler
callback_manager.register_handler('custom_webhook', CustomWebhookHandler())
```

### 3. Process Webhook

```python
from app.callbacks.callback_manager import get_callback_manager, CallbackRouter

# Get callback manager
callback_manager = get_callback_manager(db)
router = CallbackRouter(callback_manager)

# Process webhook
result = await router.route_webhook('midtrans', webhook_data)
```

### 4. Process Event

```python
# Process file event
result = await router.route_event('file_created', {
    'path': '/path/to/file.txt',
    'filename': 'file.txt'
})
```

### 5. Setup Discord Handlers

```python
import discord
from discord.ext import commands

# Create bot
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

# Setup Discord handlers
callback_manager.setup_discord_handlers(bot)
```

## Endpoint API

### Webhook Endpoints

- `POST /callbacks/webhook/midtrans` - Midtrans payment webhook
- `POST /callbacks/webhook/digiflazz` - Digiflazz PPOB webhook
- `POST /callbacks/webhook/discord` - Discord webhook
- `POST /callbacks/webhook/telegram` - Telegram webhook

### Event Endpoints

- `POST /callbacks/event/file` - File system events
- `POST /callbacks/event/discord` - Discord bot events

### Management Endpoints

- `GET /callbacks/handlers` - List registered handlers
- `GET /callbacks/stats` - Get callback statistics

## Contoh Webhook Data

### Midtrans Webhook

```json
{
  "order_id": "ORDER-123",
  "transaction_status": "settlement",
  "payment_type": "bank_transfer",
  "gross_amount": "100000.00"
}
```

### Digiflazz Webhook

```json
{
  "data": {
    "ref_id": "REF-123",
    "status": "sukses",
    "trx_id": "TRX-456",
    "message": "Transaksi berhasil",
    "sn": "1234567890"
  }
}
```

### File Event

```json
{
  "event_type": "file_created",
  "path": "/uploads/file.txt",
  "filename": "file.txt",
  "size": 1024
}
```

## Error Handling

Semua callback handlers menggunakan consistent error handling:

1. **Validation Errors**: Untuk data yang tidak valid
2. **Processing Errors**: Untuk error saat memproses callback
3. **Database Errors**: Untuk error database operations
4. **External API Errors**: Untuk error komunikasi dengan external APIs

## Logging

Setiap callback handler melakukan logging untuk:

- Incoming callbacks/events
- Processing status
- Errors dan exceptions
- Performance metrics

## Testing

### Unit Tests

```python
import pytest
from app.callbacks.payment.midtrans_callback import MidtransCallbackHandler

@pytest.mark.asyncio
async def test_midtrans_callback():
    handler = MidtransCallbackHandler(db)
    
    webhook_data = {
        "order_id": "TEST-123",
        "transaction_status": "settlement"
    }
    
    result = await handler.handle(webhook_data)
    assert result["success"] == True
```

### Integration Tests

```python
@pytest.mark.asyncio
async def test_webhook_endpoint(client):
    webhook_data = {"order_id": "TEST-123"}
    
    response = await client.post(
        "/callbacks/webhook/midtrans",
        json=webhook_data
    )
    
    assert response.status_code == 200
```

## Best Practices

1. **Idempotency**: Pastikan callback handlers idempotent
2. **Validation**: Selalu validasi data callback sebelum processing
3. **Error Handling**: Implement comprehensive error handling
4. **Logging**: Log semua callback activity untuk debugging
5. **Security**: Verify webhook signatures jika tersedia
6. **Performance**: Optimize untuk high-throughput scenarios
7. **Monitoring**: Monitor callback processing metrics

## Extensibility

Sistem ini dirancang untuk mudah diperluas:

1. **Custom Handlers**: Buat handler baru dengan extend base classes
2. **New Providers**: Tambah provider baru dengan implement interface
3. **Custom Routing**: Extend router untuk routing logic khusus
4. **Middleware**: Tambah middleware untuk cross-cutting concerns

## Configuration

Konfigurasi callback system melalui environment variables:

```env
# Midtrans
MIDTRANS_SERVER_KEY=your_server_key
MIDTRANS_CLIENT_KEY=your_client_key

# Digiflazz
DIGIFLAZZ_USERNAME=your_username
DIGIFLAZZ_API_KEY=your_api_key

# Discord
DISCORD_BOT_TOKEN=your_bot_token

# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
```
