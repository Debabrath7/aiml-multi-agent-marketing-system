import asyncio
from typing import Callable, Dict, Any

class AgentBus:
    def __init__(self):
        self.handlers = {}

    def register(self, method_name: str, handler: Callable):
        self.handlers[method_name] = handler

    async def call(self, method_name: str, params: Dict[str, Any]):
        handler = self.handlers.get(method_name)
        if not handler:
            raise Exception(f"No handler registered for {method_name}")
        if asyncio.iscoroutinefunction(handler):
            return await handler(params)
        else:
            return handler(params)

BUS = AgentBus()
