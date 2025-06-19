"""
Callback Controller
Mengelola endpoint untuk menerima callback dari berbagai provider
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging
import json

from app.api.deps import get_db
from app.callbacks.callback_manager import get_callback_manager, CallbackRouter
from app.common.responses.api_response import APIResponse

logger = logging.getLogger(__name__)


class CallbackController:
    """Controller untuk mengelola callback endpoints"""
    
    def __init__(self):
        self.router = APIRouter(prefix="/callbacks", tags=["Callbacks"])
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup callback routes"""
        
        # Webhook endpoints
        self.router.add_api_route(
            "/webhook/midtrans",
            self.midtrans_webhook,
            methods=["POST"],
            response_model=APIResponse[dict]
        )
        
        self.router.add_api_route(
            "/webhook/digiflazz",
            self.digiflazz_webhook,
            methods=["POST"],
            response_model=APIResponse[dict]
        )
        
        self.router.add_api_route(
            "/webhook/discord",
            self.discord_webhook,
            methods=["POST"],
            response_model=APIResponse[dict]
        )
        
        self.router.add_api_route(
            "/webhook/telegram",
            self.telegram_webhook,
            methods=["POST"],
            response_model=APIResponse[dict]
        )
        
        # Event endpoints
        self.router.add_api_route(
            "/event/file",
            self.file_event,
            methods=["POST"],
            response_model=APIResponse[dict]
        )
        
        self.router.add_api_route(
            "/event/discord",
            self.discord_event,
            methods=["POST"],
            response_model=APIResponse[dict]
        )
        
        # Management endpoints
        self.router.add_api_route(
            "/handlers",
            self.list_handlers,
            methods=["GET"],
            response_model=APIResponse[dict]
        )
        
        self.router.add_api_route(
            "/stats",
            self.get_stats,
            methods=["GET"],
            response_model=APIResponse[dict]
        )
    
    async def midtrans_webhook(
        self,
        request: Request,
        db: Session = Depends(get_db)
    ) -> APIResponse[dict]:
        """Handle Midtrans webhook notification"""
        try:
            # Get request body
            body = await request.body()
            webhook_data = json.loads(body.decode('utf-8'))
            
            logger.info(f"Midtrans webhook received: {webhook_data}")
            
            # Process webhook
            callback_manager = get_callback_manager(db)
            router = CallbackRouter(callback_manager)
            
            result = await router.route_webhook('midtrans', webhook_data)
            
            return APIResponse.success_response(
                data=result,
                message="Midtrans webhook processed successfully"
            )
            
        except json.JSONDecodeError:
            logger.error("Invalid JSON in Midtrans webhook")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON format"
            )
        except Exception as e:
            logger.error(f"Error processing Midtrans webhook: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Webhook processing failed: {str(e)}"
            )
    
    async def digiflazz_webhook(
        self,
        request: Request,
        db: Session = Depends(get_db)
    ) -> APIResponse[dict]:
        """Handle Digiflazz webhook notification"""
        try:
            # Get request body
            body = await request.body()
            webhook_data = json.loads(body.decode('utf-8'))
            
            logger.info(f"Digiflazz webhook received: {webhook_data}")
            
            # Process webhook
            callback_manager = get_callback_manager(db)
            router = CallbackRouter(callback_manager)
            
            result = await router.route_webhook('digiflazz', webhook_data)
            
            return APIResponse.success_response(
                data=result,
                message="Digiflazz webhook processed successfully"
            )
            
        except json.JSONDecodeError:
            logger.error("Invalid JSON in Digiflazz webhook")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON format"
            )
        except Exception as e:
            logger.error(f"Error processing Digiflazz webhook: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Webhook processing failed: {str(e)}"
            )
    
    async def discord_webhook(
        self,
        request: Request,
        db: Session = Depends(get_db)
    ) -> APIResponse[dict]:
        """Handle Discord webhook"""
        try:
            # Get request body
            body = await request.body()
            webhook_data = json.loads(body.decode('utf-8'))
            
            logger.info(f"Discord webhook received: {webhook_data}")
            
            # Process webhook
            callback_manager = get_callback_manager(db)
            router = CallbackRouter(callback_manager)
            
            result = await router.route_webhook('discord', webhook_data)
            
            return APIResponse.success_response(
                data=result,
                message="Discord webhook processed successfully"
            )
            
        except json.JSONDecodeError:
            logger.error("Invalid JSON in Discord webhook")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON format"
            )
        except Exception as e:
            logger.error(f"Error processing Discord webhook: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Webhook processing failed: {str(e)}"
            )
    
    async def telegram_webhook(
        self,
        request: Request,
        db: Session = Depends(get_db)
    ) -> APIResponse[dict]:
        """Handle Telegram webhook"""
        try:
            # Get request body
            body = await request.body()
            webhook_data = json.loads(body.decode('utf-8'))
            
            logger.info(f"Telegram webhook received: {webhook_data}")
            
            # Process webhook
            callback_manager = get_callback_manager(db)
            router = CallbackRouter(callback_manager)
            
            result = await router.route_webhook('telegram', webhook_data)
            
            return APIResponse.success_response(
                data=result,
                message="Telegram webhook processed successfully"
            )
            
        except json.JSONDecodeError:
            logger.error("Invalid JSON in Telegram webhook")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON format"
            )
        except Exception as e:
            logger.error(f"Error processing Telegram webhook: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Webhook processing failed: {str(e)}"
            )
    
    async def file_event(
        self,
        event_data: Dict[str, Any],
        db: Session = Depends(get_db)
    ) -> APIResponse[dict]:
        """Handle file system events"""
        try:
            logger.info(f"File event received: {event_data}")
            
            # Process event
            callback_manager = get_callback_manager(db)
            router = CallbackRouter(callback_manager)
            
            event_type = event_data.get('event_type', 'file_unknown')
            result = await router.route_event(event_type, event_data)
            
            return APIResponse.success_response(
                data=result,
                message="File event processed successfully"
            )
            
        except Exception as e:
            logger.error(f"Error processing file event: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Event processing failed: {str(e)}"
            )
    
    async def discord_event(
        self,
        event_data: Dict[str, Any],
        db: Session = Depends(get_db)
    ) -> APIResponse[dict]:
        """Handle Discord bot events"""
        try:
            logger.info(f"Discord event received: {event_data}")
            
            # Process event
            callback_manager = get_callback_manager(db)
            router = CallbackRouter(callback_manager)
            
            event_type = event_data.get('event_type', 'discord_unknown')
            result = await router.route_event(event_type, event_data)
            
            return APIResponse.success_response(
                data=result,
                message="Discord event processed successfully"
            )
            
        except Exception as e:
            logger.error(f"Error processing Discord event: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Event processing failed: {str(e)}"
            )
    
    async def list_handlers(
        self,
        db: Session = Depends(get_db)
    ) -> APIResponse[dict]:
        """List all registered callback handlers"""
        try:
            callback_manager = get_callback_manager(db)
            handlers = callback_manager.list_handlers()
            
            return APIResponse.success_response(
                data=handlers,
                message="Callback handlers retrieved successfully"
            )
            
        except Exception as e:
            logger.error(f"Error listing handlers: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list handlers: {str(e)}"
            )
    
    async def get_stats(
        self,
        db: Session = Depends(get_db)
    ) -> APIResponse[dict]:
        """Get callback system statistics"""
        try:
            callback_manager = get_callback_manager(db)
            stats = callback_manager.get_handler_stats()
            
            return APIResponse.success_response(
                data=stats,
                message="Callback statistics retrieved successfully"
            )
            
        except Exception as e:
            logger.error(f"Error getting stats: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get stats: {str(e)}"
            )


# Instance controller
callback_controller = CallbackController()
router = callback_controller.router
