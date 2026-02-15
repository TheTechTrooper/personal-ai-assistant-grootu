# backend/app/event_bus.py

import asyncio
from typing import List, Callable, Awaitable

# Define a type for event handlers: async function that takes a string message
EventHandler = Callable[[dict], Awaitable[None]]

class EventBus:
    def __init__(self):
        self._subscribers: List[EventHandler] = []

    def subscribe(self, handler: EventHandler):
        """Add a subscriber (e.g., a websocket connection)"""
        self._subscribers.append(handler)

    def unsubscribe(self, handler: EventHandler):
        """Remove a subscriber"""
        if handler in self._subscribers:
            self._subscribers.remove(handler)

    async def emit(self, event_type: str, data: dict):
        """Broadcast an event to all subscribers"""
        payload = {"type": event_type, "data": data}
        
        # Run all handlers concurrently
        if self._subscribers:
            await asyncio.gather(*[handler(payload) for handler in self._subscribers])

# Global instance
bus = EventBus()
