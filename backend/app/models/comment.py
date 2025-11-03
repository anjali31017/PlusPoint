from typing import Optional
from beanie import Document, Link
from pydantic import Field
from datetime import datetime

from app.models.article import ArticleModel
from app.models.users import UserModel

class CommentModel(Document):
    article_id : Link["ArticleModel"]
    user_id: Link["UserModel"]
    content: str
    parent_comment_id: Optional[Link["CommentModel"]] = None
    likes_count: int = 0
    is_deleted: bool = False
    posted_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "comments"  
