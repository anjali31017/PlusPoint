from typing import Optional, List
from beanie import Document, Indexed, Link
from pydantic import BaseModel, Field
from datetime import datetime
from app.models.users import UserModel

class PublisherInfo(BaseModel):
    publisher_user_id: Link["UserModel"]  # store MongoDB ObjectId of the user
    invited_at: datetime = Field(default_factory=datetime.now)


class FirmModel(Document):
    owner_user_id: Link["UserModel"]
    firm_name: str
    firm_username: str = Indexed(str, unique=True)
    publishers: Optional[List[PublisherInfo]] = Field(default_factory=list)
    bio: Optional[str] = None
    verification_status: str = Field(default="PENDING")  # PENDING | APPROVED | REJECTED | SUSPENDED
    trust_score: int = Field(default=0)
    violations_count: int = Field(default=0)
    is_active: bool = False
    is_deleted: bool = False
    is_verified: bool = False
    verified_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "firms"  


