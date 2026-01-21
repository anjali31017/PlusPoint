from datetime import datetime
from typing import Optional
from beanie import Document, Link
from pydantic import Field


from app.models.firm import FirmModel
from app.models.users import UserModel

class SubscriptionModel(Document):
    subscriber_id: Link["UserModel"]
    firm_id: Optional[Link["FirmModel"]] = None
    created_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "subscriptions"  
