from typing import Optional, List
from beanie import Document, Link
from pydantic import BaseModel, Field
from datetime import datetime
from app.models.users import UserModel

class PublisherInfo(BaseModel):
    publisher_user_id: Link["UserModel"]  # store MongoDB ObjectId of the user
    invited_at: datetime = Field(default_factory=datetime.now)


class FirmModel(Document):
    # firm_id: Optional[str] = Field(None, alias="_id")
    # firm_ref_if: str = = Field(default_factory=lambda: secrets.token_hex(8))
    firm_user_id: Link["UserModel"]
    firm_name: str
    publishers: Optional[List[PublisherInfo]] = Field(default_factory=list)
    # publishers: List[PublisherInfo] = []
    is_active: bool = True
    is_deleted: bool = False
    created_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "firms"  


