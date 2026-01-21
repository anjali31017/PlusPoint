# from typing import Optional, List
# from beanie import Document, Indexed, Link
# from pydantic import BaseModel, Field
# from datetime import datetime
# from app.models.users import UserModel
# from app.models.firm import FirmModel

# class PublisherModel(Document):
#     publisher_id: Link["UserModel"]
#     firm_id: Link["FirmModel"]
#     trust_factor: int = Field(default=100)
#     violations_count: int = Field(default=0)
#     is_active: bool = True
#     is_deleted: bool = False
#     is_verified: bool = True
#     verified_at: Optional[datetime] = None
#     created_at: datetime = Field(default_factory=datetime.now)

#     class Settings:
#         name = "publishers"  


