from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict, Any
import json
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class WebSocketService:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.client_subscriptions: Dict[str, List[str]] = {}
        
    async def connect(self, websocket: WebSocket, client_id: str):
        """Terima koneksi WebSocket baru"""
        await websocket.accept()
        self.active_connections.append(websocket)
        self.client_subscriptions[client_id] = []
        logger.info(f"Client {client_id} connected via WebSocket")
        
    def disconnect(self, websocket: WebSocket, client_id: str):
        """Hapus koneksi WebSocket"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if client_id in self.client_subscriptions:
            del self.client_subscriptions[client_id]
        logger.info(f"Client {client_id} disconnected")
        
    async def subscribe(self, client_id: str, topics: List[str]):
        """Subscribe client ke topik tertentu"""
        if client_id in self.client_subscriptions:
            self.client_subscriptions[client_id].extend(topics)
            
    async def broadcast_bot_status(self, bot_data: Dict[str, Any]):
        """Broadcast status bot ke semua client"""
        message = {
            "type": "bot_status_update",
            "data": bot_data,
            "timestamp": datetime.now().isoformat()
        }
        await self._broadcast_to_subscribers("bot_status", message)
        
    async def broadcast_command_log(self, log_data: Dict[str, Any]):
        """Broadcast log command baru"""
        message = {
            "type": "command_log",
            "data": log_data,
            "timestamp": datetime.now().isoformat()
        }
        await self._broadcast_to_subscribers("command_logs", message)
        
    async def _broadcast_to_subscribers(self, topic: str, message: Dict):
        """Kirim message ke client yang subscribe topik"""
        disconnected = []
        for client_id, topics in self.client_subscriptions.items():
            if topic in topics:
                websocket = self._get_websocket_by_client(client_id)
                if websocket:
                    try:
                        await websocket.send_text(json.dumps(message))
                    except WebSocketDisconnect:
                        disconnected.append(client_id)
                        
        # Cleanup disconnected clients
        for client_id in disconnected:
            if client_id in self.client_subscriptions:
                del self.client_subscriptions[client_id]
                
    def _get_websocket_by_client(self, client_id: str) -> WebSocket:
        """Helper untuk mendapatkan WebSocket berdasarkan client_id"""
        # Implementasi sederhana, bisa diperbaiki dengan mapping yang lebih baik
        return self.active_connections[0] if self.active_connections else None

# Global instance
websocket_service = WebSocketService()
