
from bson import ObjectId
from app.models.notification import NotificationModel


class NotificationController:
    
    async def save_notification(self, notification_data : dict) -> NotificationModel | None:
        try:
            notification = NotificationModel(
                send_to= ObjectId(notification_data["send_to"]),
                message= notification_data["message"],
                sent= notification_data["sent"],
                type=notification_data["type"]
            )
            await notification.insert()
            return notification
        except Exception as e:
            print(f"Error sending notification: {e}")
            return None