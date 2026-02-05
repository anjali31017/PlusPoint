from datetime import datetime
from beanie import Document, Link
from pydantic import Field

from app.models.users import UserModel
from enum import Enum


class NotificationStatus(str, Enum):
    ARTICLE = "ARTICLE"
    LIKE = "LIKE"
    COMMENT = "COMMENT"
    FOLLOW = "FOLLOW"
    EVENT = "EVENT"
    ADMIN = "ADMIN"
    ENDORSE = "ENDORSE"
    

class NotificationModel(Document):
    send_to: Link["UserModel"]
    message: dict
    type: NotificationStatus = NotificationStatus.EVENT
    sent: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    class Settings:
        name = "notifications"