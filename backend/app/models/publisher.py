from typing import Optional, List
from beanie import Document, Indexed, Link
from pydantic import BaseModel, Field
from datetime import datetime
from app.models.users import UserModel
from app.models.firm import FirmModel

class PublisherModel(Document):
    publisher_id: Link["UserModel"]
    firm_id: Link["FirmModel"]
    verification_status: str = Field(default="UNDER_REVIEW")  # PENDING | APPROVED | REJECTED | SUSPENDED
    trust_score: int = Field(default=0)
    violations_count: int = Field(default=0)
    is_active: bool = False
    is_deleted: bool = False
    is_verified: bool = False
    verified_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "publishers"  


