import asyncio
from typing import Dict

class SSEManager:
    def __init__(self):
        self.connections: Dict[str, asyncio.Queue] = {}

    async def connect(self, user_id: str) -> asyncio.Queue:
        try:
            queue = asyncio.Queue()
            self.connections[user_id] = queue
            return queue
        except Exception as e:
            print(f"Error connecting user {user_id}: {e}")
            raise

    def disconnect(self, user_id: str):
        try:
            self.connections.pop(user_id, None)
        except Exception as e:
            print(f"Error disconnecting user {user_id}: {e}")

    async def send_to_user(self, user_id: str, message: dict):
        try:
            if user_id in self.connections:
                await self.connections[user_id].put(message)
        except Exception as e:
            print(f"Error sending message to user {user_id}: {e}")
            
    async def broadcast(self, message: dict):
        try:
            for q in self.connections.values():
                await q.put(message)
        except Exception as e:
            print(f"Error broadcasting message: {e}")