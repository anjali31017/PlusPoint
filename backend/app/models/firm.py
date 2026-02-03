from typing import Optional, List
from beanie import Document, Indexed, Link
from pydantic import BaseModel, Field
from datetime import datetime
from app.models.users import UserModel
from enum import Enum
# class PublisherInfo(BaseModel):
#     publisher_user_id: Link["UserModel"]  # store MongoDB ObjectId of the user

class VerificationStatus(str, Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    SUSPENDED = "SUSPENDED"
    

class FirmModel(Document):
    owner_user_id: Link["UserModel"]
    firm_name: str
    firm_username: str = Indexed(str, unique=True)
    # publishers: Optional[List[PublisherInfo]] = Field(default_factory=list)
    bio: Optional[str] = None
    verification_status: VerificationStatus = VerificationStatus.APPROVED # PENDING | APPROVED | REJECTED | SUSPENDED
    trust_factor: float = Field(default=100)
    violations_count: int = Field(default=0)
    follow_count: int = 0
    report_count: int = 0
    endorse_count: int = 0
    delete_reason: Optional[str] = None
    is_active: bool = True
    is_deleted: bool = False
    created_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "firms"  


