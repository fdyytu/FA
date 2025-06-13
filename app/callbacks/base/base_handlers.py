"""
Base classes untuk callback handlers
Menyediakan interface dan implementasi dasar untuk semua callback
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class BaseCallbackHandler(ABC):
    """Base class untuk semua callback handlers"""
    
    def __init__(self, name: str):
        self.name = name
        self.created_at = datetime.now()
        
    @abstractmethod
    async def handle(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle callback data - harus diimplementasikan oleh subclass"""
        pass
    
    def validate_data(self, data: Dict[str, Any], required_fields: list) -> bool:
        """Validasi data callback"""
        for field in required_fields:
            if field not in data:
                logger.error(f"Missing required field: {field}")
                return False
        return True
    
    def log_callback(self, data: Dict[str, Any], status: str, message: str = ""):
        """Log callback activity"""
        logger.info(f"Callback {self.name} - Status: {status} - Data: {data} - Message: {message}")


class WebhookCallbackHandler(BaseCallbackHandler):
    """Base class untuk webhook callbacks"""
    
    def __init__(self, name: str, webhook_type: str):
        super().__init__(name)
        self.webhook_type = webhook_type
    
    async def process_webhook(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process webhook request"""
        try:
            # Log incoming webhook
            self.log_callback(request_data, "RECEIVED", f"Webhook {self.webhook_type} received")
            
            # Handle the webhook
            result = await self.handle(request_data)
            
            # Log success
            self.log_callback(request_data, "SUCCESS", f"Webhook {self.webhook_type} processed successfully")
            
            return result
            
        except Exception as e:
            # Log error
            self.log_callback(request_data, "ERROR", f"Webhook {self.webhook_type} failed: {str(e)}")
            raise


class EventCallbackHandler(BaseCallbackHandler):
    """Base class untuk event callbacks"""
    
    def __init__(self, name: str, event_type: str):
        super().__init__(name)
        self.event_type = event_type
    
    async def process_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process event"""
        try:
            # Log incoming event
            self.log_callback(event_data, "RECEIVED", f"Event {self.event_type} received")
            
            # Handle the event
            result = await self.handle(event_data)
            
            # Log success
            self.log_callback(event_data, "SUCCESS", f"Event {self.event_type} processed successfully")
            
            return result
            
        except Exception as e:
            # Log error
            self.log_callback(event_data, "ERROR", f"Event {self.event_type} failed: {str(e)}")
            raise


class CallbackRegistry:
    """Registry untuk mengelola callback handlers"""
    
    def __init__(self):
        self._handlers: Dict[str, BaseCallbackHandler] = {}
    
    def register(self, callback_type: str, handler: BaseCallbackHandler):
        """Register callback handler"""
        self._handlers[callback_type] = handler
        logger.info(f"Registered callback handler: {callback_type}")
    
    def get_handler(self, callback_type: str) -> Optional[BaseCallbackHandler]:
        """Get callback handler by type"""
        return self._handlers.get(callback_type)
    
    def list_handlers(self) -> Dict[str, str]:
        """List all registered handlers"""
        return {k: v.name for k, v in self._handlers.items()}


# Global callback registry
callback_registry = CallbackRegistry()
