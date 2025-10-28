from typing import Optional, List
from beanie import Document, Indexed
from pydantic import BaseModel, Field
from datetime import datetime
from passlib.hash import bcrypt  

class Comment(Document):
    article_id = Link["Article"]
    user_id: Link["User"]
    content: str
    parent_comment_id: Optional[Link["Comment"]] = None
    likes_count: int = 0
    is_deleted: bool = False
    posted_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "comments"  
