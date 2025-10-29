from beanie import Document, Link
from pydantic import Field
from datetime import datetime

class SubscriptionModel(Document):
    firm_id: Link["FirmModel"]
    subscriber_id: Link["UserModel"]
    created_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "subscriptions"  
