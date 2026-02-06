import asyncio
from typing import Dict, List

from bson import ObjectId

from app.models.notification import NotificationModel
from app.controller.notification_controller import NotificationController

notification_controller = NotificationController()

class SSEManager:
    def __init__(self):
        self.connections: Dict[str, Dict[str, List[asyncio.Queue]]] = {
            "notifications": {},
            "feed": {}
        }
        # self.connections: Dict[str, asyncio.Queue] = {}
    
    async def connect(self, channel: str, user_id: str) -> asyncio.Queue:
        try:
            queue = asyncio.Queue()
            if user_id not in self.connections[channel]:
                self.connections[channel][user_id] = []
            
            self.connections[channel][user_id].append(queue)
            print(f"[{channel}] User {user_id} connected " f"({len(self.connections[channel][user_id])} connections)")
    
            # self.connections[user_id] = queue
            return queue
        except Exception as e:
            print(f"Error connecting user {user_id}: {e}")
            raise

    async def disconnect(self, channel:str, user_id: str, queue: asyncio.Queue):
        if user_id in self.connections[channel]:
            try:
                self.connections[channel][user_id].remove(queue)

                if not self.connections[channel][user_id]:
                    del self.connections[channel][user_id]

                print(f"[{channel}] Disconnected one SSE for {user_id}")
            except ValueError:
                pass
            except Exception as e:
                print(f"Error disconnecting user {user_id}: {e}")

    async def send_to_user(self, user_id: str, message: dict, type: str):
        try:
            notification_data = {
                "send_to": user_id,
                "message": message,
                "type": type,
                "sent": True
            }

            if user_id in self.connections["notifications"]:
                for queue in self.connections["notifications"][user_id]:
                    await queue.put(notification_data)

                asyncio.create_task(
                    notification_controller.save_notification(notification_data)
                )
            else:
                notification_data["sent"] = False
                await notification_controller.save_notification(notification_data)

        except Exception as e:
            print(f"Error sending message to user {user_id}: {e}")
            
    async def broadcast(self, message: dict):
        try:
            for queues in self.connections["feed"].values():
                for queue in queues:
                    await queue.put(message)
            # for q in self.connections.values():
            #     await q.put(message)
        except Exception as e:
            print(f"Error broadcasting message: {e}")
            
            
sse_connection_manager = SSEManager()