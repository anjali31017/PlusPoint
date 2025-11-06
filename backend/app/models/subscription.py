from typing import List, Optional
from beanie import Document, Link
from pydantic import Field
from datetime import datetime

from app.models.firm import FirmModel
from app.models.users import UserModel

class SubscriptionModel(Document):
    subscriber_id: Link["UserModel"]
    firm_ids: Optional[List[str]] = []
    publisher_ids: Optional[List[str]] = []

    class Settings:
        name = "subscriptions"  
