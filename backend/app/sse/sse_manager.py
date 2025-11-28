import asyncio
from typing import Dict

from app.models.notification import NotificationModel
from app.controller.notification_controller import NotificationController

notification_controller = NotificationController()

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
            notification_data = {
                    "user_id": user_id,
                    "message": message,
                    "sent": True
                }
            if user_id in self.connections:
                print(f"Sending message to user {user_id}")
                await self.connections[user_id].put(message)
                await notification_controller.save_notification(notification_data)
            else:
                print(f"User {user_id} not connected")
                notification_data["sent"] = False
                await notification_controller.save_notification(notification_data)
        except Exception as e:
            print(f"Error sending message to user {user_id}: {e}")
            
    async def broadcast(self, message: dict):
        try:
            for q in self.connections.values():
                await q.put(message)
        except Exception as e:
            print(f"Error broadcasting message: {e}")