"""
Contoh penggunaan Callback System
Demonstrasi cara menggunakan callback system yang telah dibuat
"""
import asyncio
from sqlalchemy.orm import Session
from app.callbacks import (
    initialize_callbacks,
    get_callback_manager,
    CallbackRouter,
    MidtransCallbackHandler,
    DigiflazzCallbackHandler,
    FileMonitorCallbackHandler
)


async def example_midtrans_webhook():
    """Contoh penggunaan Midtrans webhook callback"""
    print("=== Contoh Midtrans Webhook ===")
    
    # Simulasi data webhook dari Midtrans
    webhook_data = {
        "order_id": "ORDER-123456",
        "transaction_status": "settlement",
        "payment_type": "bank_transfer",
        "gross_amount": "100000.00",
        "transaction_time": "2023-12-01 10:00:00",
        "signature_key": "dummy_signature"
    }
    
    # Initialize callback system (dalam aplikasi nyata, ini dilakukan saat startup)
    # db = get_db_session()  # Dapatkan database session
    # callback_manager = initialize_callbacks(db)
    
    # Simulasi processing webhook
    print(f"Processing Midtrans webhook: {webhook_data['order_id']}")
    print(f"Transaction status: {webhook_data['transaction_status']}")
    print(f"Amount: Rp {webhook_data['gross_amount']}")
    
    # Dalam implementasi nyata:
    # router = CallbackRouter(callback_manager)
    # result = await router.route_webhook('midtrans', webhook_data)
    # print(f"Result: {result}")


async def example_digiflazz_webhook():
    """Contoh penggunaan Digiflazz webhook callback"""
    print("\n=== Contoh Digiflazz Webhook ===")
    
    # Simulasi data webhook dari Digiflazz
    webhook_data = {
        "data": {
            "ref_id": "REF-789012",
            "status": "sukses",
            "trx_id": "TRX-345678",
            "message": "Transaksi berhasil",
            "sn": "1234567890123456",
            "product_name": "Pulsa Telkomsel 10K"
        }
    }
    
    print(f"Processing Digiflazz webhook: {webhook_data['data']['ref_id']}")
    print(f"Status: {webhook_data['data']['status']}")
    print(f"Product: {webhook_data['data']['product_name']}")
    print(f"Serial Number: {webhook_data['data']['sn']}")
    
    # Dalam implementasi nyata:
    # router = CallbackRouter(callback_manager)
    # result = await router.route_webhook('digiflazz', webhook_data)
    # print(f"Result: {result}")


async def example_file_event():
    """Contoh penggunaan file event callback"""
    print("\n=== Contoh File Event ===")
    
    # Simulasi file event
    file_event_data = {
        "event_type": "file_created",
        "path": "/uploads/documents/invoice_123.pdf",
        "filename": "invoice_123.pdf",
        "size": 2048,
        "timestamp": "2023-12-01T10:30:00Z"
    }
    
    print(f"Processing file event: {file_event_data['event_type']}")
    print(f"File: {file_event_data['filename']}")
    print(f"Size: {file_event_data['size']} bytes")
    
    # Dalam implementasi nyata:
    # router = CallbackRouter(callback_manager)
    # result = await router.route_event('file_created', file_event_data)
    # print(f"Result: {result}")


async def example_discord_event():
    """Contoh penggunaan Discord event callback"""
    print("\n=== Contoh Discord Event ===")
    
    # Simulasi Discord event
    discord_event_data = {
        "event_type": "on_message",
        "event_data": {
            "author": "User#1234",
            "content": "Hello bot!",
            "guild": "Test Server",
            "channel": "general"
        }
    }
    
    print(f"Processing Discord event: {discord_event_data['event_type']}")
    print(f"Author: {discord_event_data['event_data']['author']}")
    print(f"Message: {discord_event_data['event_data']['content']}")
    print(f"Guild: {discord_event_data['event_data']['guild']}")
    
    # Dalam implementasi nyata:
    # router = CallbackRouter(callback_manager)
    # result = await router.route_event('discord_message', discord_event_data)
    # print(f"Result: {result}")


async def example_custom_callback():
    """Contoh membuat custom callback handler"""
    print("\n=== Contoh Custom Callback ===")
    
    from app.callbacks.base.base_handlers import WebhookCallbackHandler
    from typing import Dict, Any
    
    class CustomWebhookHandler(WebhookCallbackHandler):
        """Custom webhook handler untuk provider khusus"""
        
        def __init__(self):
            super().__init__("CustomWebhook", "custom_provider")
        
        async def handle(self, data: Dict[str, Any]) -> Dict[str, Any]:
            """Handle custom webhook"""
            print(f"Processing custom webhook: {data}")
            
            # Custom logic di sini
            transaction_id = data.get('transaction_id')
            status = data.get('status')
            
            # Simulasi processing
            if status == 'success':
                print(f"Transaction {transaction_id} berhasil diproses")
                return {
                    'success': True,
                    'message': f'Transaction {transaction_id} processed successfully',
                    'transaction_id': transaction_id
                }
            else:
                print(f"Transaction {transaction_id} gagal")
                return {
                    'success': False,
                    'message': f'Transaction {transaction_id} failed',
                    'transaction_id': transaction_id
                }
    
    # Buat instance handler
    custom_handler = CustomWebhookHandler()
    
    # Simulasi data webhook
    webhook_data = {
        'transaction_id': 'TXN-999888',
        'status': 'success',
        'amount': 50000,
        'provider': 'custom_provider'
    }
    
    # Process webhook
    result = await custom_handler.handle(webhook_data)
    print(f"Custom webhook result: {result}")


async def example_callback_manager_usage():
    """Contoh penggunaan Callback Manager"""
    print("\n=== Contoh Callback Manager ===")
    
    # Dalam implementasi nyata, ini akan menggunakan database session
    # db = get_db_session()
    # callback_manager = get_callback_manager(db)
    
    # Simulasi list handlers
    print("Registered handlers:")
    handlers = {
        'midtrans_payment': 'MidtransCallback',
        'file_monitor': 'FileMonitorCallback',
        'file_upload': 'FileUploadCallback'
    }
    
    for callback_type, handler_name in handlers.items():
        print(f"  - {callback_type}: {handler_name}")
    
    # Simulasi stats
    print("\nCallback statistics:")
    stats = {
        'total_handlers': len(handlers),
        'handlers': {
            'midtrans_payment': {
                'name': 'MidtransCallback',
                'type': 'WebhookCallbackHandler',
                'created_at': '2023-12-01T09:00:00Z'
            },
            'file_monitor': {
                'name': 'FileMonitorCallback',
                'type': 'EventCallbackHandler',
                'created_at': '2023-12-01T09:00:00Z'
            }
        }
    }
    
    print(f"Total handlers: {stats['total_handlers']}")
    for handler_type, handler_info in stats['handlers'].items():
        print(f"  {handler_type}: {handler_info['name']} ({handler_info['type']})")


async def main():
    """Main function untuk menjalankan semua contoh"""
    print("Callback System Examples")
    print("=" * 50)
    
    # Jalankan semua contoh
    await example_midtrans_webhook()
    await example_digiflazz_webhook()
    await example_file_event()
    await example_discord_event()
    await example_custom_callback()
    await example_callback_manager_usage()
    
    print("\n" + "=" * 50)
    print("Semua contoh selesai dijalankan!")


if __name__ == "__main__":
    # Jalankan contoh
    asyncio.run(main())
