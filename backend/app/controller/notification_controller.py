
from app.models.notification import NotificationModel


class NotificationController:
    
    async def save_notification(self, notification_data : dict) -> NotificationModel | None:
        try:
            notification = NotificationModel(
                user_id= notification_data["user_id"],
                message= notification_data["message"],
                sent= notification_data["sent"]
            )
            await notification.insert()
            return notification
        except Exception as e:
            print(f"Error sending notification: {e}")
            return None