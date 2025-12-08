from typing import List, Optional
from beanie import Document, Link
from pydantic import Field
from datetime import datetime
from app.models.firm import FirmModel
from app.models.users import UserModel

class ArticleModel(Document):
    firm_id : Link["FirmModel"]
    publisher_id: Link["UserModel"]
    title: str
    content: str
    summary: Optional[str] = None
    category: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    like_count: int = 0
    hot_topic: bool = False
    is_deleted: bool = False
    published_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "articles"  
#view counts, comments, shares can be added later

class ArticleLikeModel(Document):
    article_id : Link["ArticleModel"]
    user_id: Link["UserModel"]
    created_at: datetime = Field(default_factory=datetime.now)
    class Settings:
        name = "likes"  
