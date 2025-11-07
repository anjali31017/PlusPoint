from typing import Optional
from beanie import Document, Link


from app.models.firm import FirmModel
from app.models.users import UserModel

class SubscriptionModel(Document):
    subscriber_id: Link["UserModel"]
    firm_id: Optional[Link["FirmModel"]] = None
    publisher_id: Optional[Link["UserModel"]] = None

    class Settings:
        name = "subscriptions"  
