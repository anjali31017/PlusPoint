from beanie import Document, Link

from app.models.users import UserModel
from enum import Enum


class NotificationStatus(str, Enum):
    ARTICLE = "ARTICLE"
    LIKE = "LIKE"
    COMMENT = "COMMENT"
    FOLLOW = "FOLLOW"
    EVENT = "EVENT"
    ADMIN = "ADMIN"
    

class NotificationModel(Document):
    send_to: Link["UserModel"]
    message: dict
    type: NotificationStatus = NotificationStatus.EVENT
    sent: bool = False
    class Settings:
        name = "notifications"