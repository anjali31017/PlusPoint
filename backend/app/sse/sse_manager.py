import asyncio
from typing import Dict

from bson import ObjectId

from app.models.notification import NotificationModel
from app.controller.notification_controller import NotificationController

notification_controller = NotificationController()

class SSEManager:
    def __init__(self):
        self.connections: Dict[str, asyncio.Queue] = {}
        
    # async def connect(self, user_id: str) -> asyncio.Queue:
    #     """
    #     Connect user to SSE and replay any missed notifications.
    #     """
    #     queue = asyncio.Queue()
    #     self.connections[user_id] = queue

    #     # ---- Replay missed notifications ----
    #     try:
    #         unsent_notifications = await NotificationModel.find(
    #             {"send_to": ObjectId(user_id), "sent": False}
    #         ).to_list()

    #         for n in unsent_notifications:
    #             await queue.put({
    #                 "message": n.message,
    #                 "type": n.type,
    #                 "_id": str(n.id)
    #             })
    #             await NotificationModel.find_one(n.id).update({"$set": {"sent": True}})
    #         if unsent_notifications:
    #             print(f"Replayed {len(unsent_notifications)} missed notifications for user {user_id}")
    #     except Exception as e:
    #         print(f"Error replaying notifications for {user_id}: {e}")
    #     return queue
    
    async def connect(self, user_id: str) -> asyncio.Queue:
        try:
            queue = asyncio.Queue()
            if user_id not in self.connections:
                self.connections[user_id] = []
            
            self.connections[user_id].append(queue)
            print(f"User {user_id} now has {len(self.connections[user_id])} connections")
    
            # self.connections[user_id] = queue
            return queue
        except Exception as e:
            print(f"Error connecting user {user_id}: {e}")
            raise

    async def disconnect(self, user_id: str, queue: asyncio.Queue):
        if user_id in self.connections:
            try:
                self.connections[user_id].remove(queue)

                if not self.connections[user_id]:
                    del self.connections[user_id]

                print(f"Disconnected one SSE for {user_id}")
            except ValueError:
                pass
            # try:
            #     self.connections.pop(user_id, None)
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

            if user_id in self.connections:
                for queue in self.connections[user_id]:
                    await queue.put(notification_data)

                asyncio.create_task(
                    notification_controller.save_notification(notification_data)
                )
            else:
                notification_data["sent"] = False
                await notification_controller.save_notification(notification_data)

        except Exception as e:
            print(f"Error sending message to user {user_id}: {e}")
    
    
    
    # async def send_to_user(self, user_id: str, message: dict, type: str):
    #     try:
    #         notification_data = {
    #                 "send_to": user_id,
    #                 "message": message,
    #                 "type": type,
    #                 "sent": True
    #             }
    #         if user_id in self.connections:
    #             print(f"Sending message to user {user_id}")
    #             await self.connections[user_id].put(notification_data)
                
    #             asyncio.create_task(notification_controller.save_notification(notification_data))
    #             # await notification_controller.save_notification(notification_data)
    #         else:
    #             print(f"User {user_id} not connected")
    #             notification_data["sent"] = False
    #             await notification_controller.save_notification(notification_data)
    #     except Exception as e:
    #         print(f"Error sending message to user {user_id}: {e}")
            
    async def broadcast(self, message: dict):
        try:
            for q in self.connections.values():
                await q.put(message)
        except Exception as e:
            print(f"Error broadcasting message: {e}")
            
            
sse_connection_manager = SSEManager()