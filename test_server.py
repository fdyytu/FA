"""
Test Server untuk Callback System
Server sederhana untuk testing callback endpoints
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import logging
from typing import Dict, Any

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="FA Backend Callback System Test",
    description="Test server untuk callback system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock database session
class MockDB:
    def __init__(self):
        self.data = {}
    
    def commit(self):
        pass
    
    def rollback(self):
        pass

mock_db = MockDB()

# Mock callback handlers untuk testing
class MockCallbackHandler:
    def __init__(self, name: str):
        self.name = name
    
    async def handle(self, data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"Processing {self.name} callback: {data}")
        return {
            "success": True,
            "message": f"{self.name} callback processed successfully",
            "handler": self.name,
            "data": data
        }

# Mock callback manager
class MockCallbackManager:
    def __init__(self):
        self.handlers = {
            'midtrans_payment': MockCallbackHandler('Midtrans'),
            'digiflazz_ppob': MockCallbackHandler('Digiflazz'),
            'file_monitor': MockCallbackHandler('FileMonitor'),
            'discord_event': MockCallbackHandler('Discord')
        }
    
    async def process_webhook(self, webhook_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        handler_map = {
            'midtrans': 'midtrans_payment',
            'digiflazz': 'digiflazz_ppob'
        }
        
        handler_key = handler_map.get(webhook_type)
        if handler_key and handler_key in self.handlers:
            return await self.handlers[handler_key].handle(data)
        else:
            return {
                "success": False,
                "message": f"No handler found for webhook type: {webhook_type}"
            }
    
    async def process_event(self, event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        if event_type.startswith('file_'):
            return await self.handlers['file_monitor'].handle(data)
        elif event_type.startswith('discord_'):
            return await self.handlers['discord_event'].handle(data)
        else:
            return {
                "success": False,
                "message": f"No handler found for event type: {event_type}"
            }
    
    def list_handlers(self) -> Dict[str, str]:
        return {k: v.name for k, v in self.handlers.items()}
    
    def get_handler_stats(self) -> Dict[str, Any]:
        return {
            'total_handlers': len(self.handlers),
            'handlers': {k: {'name': v.name, 'type': 'MockHandler'} for k, v in self.handlers.items()}
        }

callback_manager = MockCallbackManager()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "FA Backend Callback System Test Server",
        "version": "1.0.0",
        "endpoints": {
            "webhooks": [
                "/callbacks/webhook/midtrans",
                "/callbacks/webhook/digiflazz",
                "/callbacks/webhook/discord",
                "/callbacks/webhook/telegram"
            ],
            "events": [
                "/callbacks/event/file",
                "/callbacks/event/discord"
            ],
            "management": [
                "/callbacks/handlers",
                "/callbacks/stats"
            ]
        }
    }

@app.post("/callbacks/webhook/midtrans")
async def midtrans_webhook(request: Request):
    """Handle Midtrans webhook notification"""
    try:
        body = await request.body()
        webhook_data = json.loads(body.decode('utf-8'))
        
        logger.info(f"Midtrans webhook received: {webhook_data}")
        
        result = await callback_manager.process_webhook('midtrans', webhook_data)
        
        return {
            "success": True,
            "message": "Midtrans webhook processed successfully",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Error processing Midtrans webhook: {str(e)}")
        return {
            "success": False,
            "message": f"Webhook processing failed: {str(e)}"
        }

@app.post("/callbacks/webhook/digiflazz")
async def digiflazz_webhook(request: Request):
    """Handle Digiflazz webhook notification"""
    try:
        body = await request.body()
        webhook_data = json.loads(body.decode('utf-8'))
        
        logger.info(f"Digiflazz webhook received: {webhook_data}")
        
        result = await callback_manager.process_webhook('digiflazz', webhook_data)
        
        return {
            "success": True,
            "message": "Digiflazz webhook processed successfully",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Error processing Digiflazz webhook: {str(e)}")
        return {
            "success": False,
            "message": f"Webhook processing failed: {str(e)}"
        }

@app.post("/callbacks/webhook/discord")
async def discord_webhook(webhook_data: Dict[str, Any]):
    """Handle Discord webhook"""
    try:
        logger.info(f"Discord webhook received: {webhook_data}")
        
        # Mock Discord webhook processing
        result = {
            "success": True,
            "message": "Discord webhook sent successfully",
            "webhook_url": webhook_data.get('webhook_url', 'mock_url')
        }
        
        return {
            "success": True,
            "message": "Discord webhook processed successfully",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Error processing Discord webhook: {str(e)}")
        return {
            "success": False,
            "message": f"Webhook processing failed: {str(e)}"
        }

@app.post("/callbacks/webhook/telegram")
async def telegram_webhook(webhook_data: Dict[str, Any]):
    """Handle Telegram webhook"""
    try:
        logger.info(f"Telegram webhook received: {webhook_data}")
        
        # Mock Telegram webhook processing
        result = {
            "success": True,
            "message": "Telegram message sent successfully",
            "chat_id": webhook_data.get('chat_id', 'mock_chat_id')
        }
        
        return {
            "success": True,
            "message": "Telegram webhook processed successfully",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Error processing Telegram webhook: {str(e)}")
        return {
            "success": False,
            "message": f"Webhook processing failed: {str(e)}"
        }

@app.post("/callbacks/event/file")
async def file_event(event_data: Dict[str, Any]):
    """Handle file system events"""
    try:
        logger.info(f"File event received: {event_data}")
        
        event_type = event_data.get('event_type', 'file_unknown')
        result = await callback_manager.process_event(event_type, event_data)
        
        return {
            "success": True,
            "message": "File event processed successfully",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Error processing file event: {str(e)}")
        return {
            "success": False,
            "message": f"Event processing failed: {str(e)}"
        }

@app.post("/callbacks/event/discord")
async def discord_event(event_data: Dict[str, Any]):
    """Handle Discord bot events"""
    try:
        logger.info(f"Discord event received: {event_data}")
        
        event_type = event_data.get('event_type', 'discord_unknown')
        result = await callback_manager.process_event(event_type, event_data)
        
        return {
            "success": True,
            "message": "Discord event processed successfully",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Error processing Discord event: {str(e)}")
        return {
            "success": False,
            "message": f"Event processing failed: {str(e)}"
        }

@app.get("/callbacks/handlers")
async def list_handlers():
    """List all registered callback handlers"""
    try:
        handlers = callback_manager.list_handlers()
        
        return {
            "success": True,
            "message": "Callback handlers retrieved successfully",
            "data": handlers
        }
        
    except Exception as e:
        logger.error(f"Error listing handlers: {str(e)}")
        return {
            "success": False,
            "message": f"Failed to list handlers: {str(e)}"
        }

@app.get("/callbacks/stats")
async def get_stats():
    """Get callback system statistics"""
    try:
        stats = callback_manager.get_handler_stats()
        
        return {
            "success": True,
            "message": "Callback statistics retrieved successfully",
            "data": stats
        }
        
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return {
            "success": False,
            "message": f"Failed to get stats: {str(e)}"
        }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Callback system is running",
        "handlers_count": len(callback_manager.handlers)
    }

if __name__ == "__main__":
    uvicorn.run(
        "test_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
