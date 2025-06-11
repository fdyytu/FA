from typing import List, Callable, Dict
import asyncio
from app.models.file_event import FileEvent

class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        
    async def publish(self, event_type: str, event: FileEvent):
        """Publish an event to all subscribers"""
        if event_type in self._subscribers:
            for subscriber in self._subscribers[event_type]:
                await subscriber(event)
    
    def subscribe(self, event_type: str, callback: Callable):
        """Subscribe to an event type"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
    
    def unsubscribe(self, event_type: str, callback: Callable):
        """Unsubscribe from an event type"""
        if event_type in self._subscribers:
            self._subscribers[event_type].remove(callback)

event_bus = EventBus()