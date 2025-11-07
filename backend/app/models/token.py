from beanie import Document, Indexed, Link
from pydantic import Field
from datetime import datetime

from app.models.users import UserModel

class RefreshTokenModel(Document):
    user_id: Link["UserModel"]
    token: str= Indexed(str, unique=True)
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: datetime
    is_revoked: bool = False

    class Settings:
        name = "refresh_tokens"
