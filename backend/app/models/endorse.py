from datetime import datetime
from typing import Optional
from beanie import Document, Link
from pydantic import Field
from pydantic import BaseModel

from app.models.firm import FirmModel
from app.models.users import UserModel
from app.models.article import ArticleModel

class EndorsementModel(Document):
    user_id: Link["UserModel"]
    firm_id: Optional[Link["FirmModel"]] = None
    article_id: Optional[Link["ArticleModel"]] = None
    created_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "endorsements"  

