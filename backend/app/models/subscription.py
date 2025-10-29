from beanie import Document, Link
from pydantic import Field
from datetime import datetime

class Subscription(Document):
    firm_id: Link["Firm"]
    subscriber_id: Link["User"]
    created_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "subscriptions"  
