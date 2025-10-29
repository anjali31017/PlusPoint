from typing import Optional, List
from beanie import Document, Indexed, Link
from pydantic import BaseModel, Field
from datetime import datetime
from backend.app.models.firm import FirmModel
from backend.app.models.users import UserModel

class ArticleModel(Document):
    firm_id : Link["FirmModel"]
    publisher_id: Link["UserModel"]
    title: str
    content: str
    category: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    liked_by: List[Link["UserModel"]] = Field(default_factory=list)
    hot_topic: bool = False
    is_deleted: bool = False
    published_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "articles"  


#view counts, comments, shares can be added later