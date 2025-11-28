from beanie import Document, Link

from app.models.users import UserModel


class NotificationModel(Document):
    user_id: Link["UserModel"]
    message: dict
    sent: bool = False
    class Settings:
        name = "notifications"