from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Optional
import uuid
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # Mapping client_id ke WebSocket connection
        self.connections: Dict[str, WebSocket] = {}
        # Mapping client_id ke list topik yang di-subscribe
        self.subscriptions: Dict[str, List[str]] = {}
        
    async def connect(self, websocket: WebSocket) -> str:
        """Accept koneksi baru dan return client_id"""
        await websocket.accept()
        client_id = str(uuid.uuid4())
        self.connections[client_id] = websocket
        self.subscriptions[client_id] = []
        logger.info(f"New WebSocket connection: {client_id}")
        return client_id
        
    def disconnect(self, client_id: str):
        """Hapus koneksi client"""
        if client_id in self.connections:
            del self.connections[client_id]
        if client_id in self.subscriptions:
            del self.subscriptions[client_id]
        logger.info(f"Client disconnected: {client_id}")
        
    async def subscribe_to_topics(self, client_id: str, topics: List[str]):
        """Subscribe client ke topik-topik tertentu"""
        if client_id in self.subscriptions:
            # Tambah topik baru tanpa duplikasi
            current_topics = set(self.subscriptions[client_id])
            new_topics = set(topics)
            self.subscriptions[client_id] = list(current_topics.union(new_topics))
            
    async def unsubscribe_from_topics(self, client_id: str, topics: List[str]):
        """Unsubscribe client dari topik tertentu"""
        if client_id in self.subscriptions:
            current_topics = set(self.subscriptions[client_id])
            remove_topics = set(topics)
            self.subscriptions[client_id] = list(current_topics - remove_topics)
            
    async def broadcast_to_topic(self, topic: str, message: dict):
        """Broadcast message ke semua client yang subscribe topik"""
        disconnected_clients = []
        
        for client_id, topics in self.subscriptions.items():
            if topic in topics and client_id in self.connections:
                try:
                    websocket = self.connections[client_id]
                    await websocket.send_text(json.dumps(message))
                except WebSocketDisconnect:
                    disconnected_clients.append(client_id)
                except Exception as e:
                    logger.error(f"Error sending to {client_id}: {e}")
                    disconnected_clients.append(client_id)
                    
        # Cleanup disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)
            
    async def send_to_client(self, client_id: str, message: dict):
        """Kirim message ke client tertentu"""
        if client_id in self.connections:
            try:
                websocket = self.connections[client_id]
                await websocket.send_text(json.dumps(message))
                return True
            except WebSocketDisconnect:
                self.disconnect(client_id)
                return False
        return False
        
    def get_active_connections_count(self) -> int:
        """Return jumlah koneksi aktif"""
        return len(self.connections)
        
    def get_topic_subscribers(self, topic: str) -> List[str]:
        """Return list client_id yang subscribe ke topik"""
        subscribers = []
        for client_id, topics in self.subscriptions.items():
            if topic in topics:
                subscribers.append(client_id)
        return subscribers

# Global instance
connection_manager = ConnectionManager()
