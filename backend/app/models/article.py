from typing import List, Optional
from beanie import Document, Link
from pydantic import Field
from datetime import datetime
from app.models.firm import FirmModel
from app.models.users import UserModel
from enum import Enum


class ArticleStatus(str, Enum):
    DRAFT = "DRAFT"
    PENDING_REVIEW = "PENDING_REVIEW"
    PUBLISHED = "PUBLISHED"
    REJECTED = "REJECTED"
    ARCHIVED = "ARCHIVED"


class ArticleModel(Document):
    firm_id: Link["FirmModel"]
    publisher_id: Link["UserModel"]
    title: str
    content: str
    content_text: Optional[str] = None
    summary: Optional[str] = None
    category: Optional[List[str]] = Field(default_factory=list)
    tags: Optional[List[str]] = Field(default_factory=list)
    cover_page: Optional[str] = None
    status: ArticleStatus = ArticleStatus.DRAFT
    trust_score_snapshot: Optional[float] = None
    moderation_required: bool = False
    delete_reason: Optional[str] = None
    like_count: int = 0
    report_count: int = 0
    endorse_count: int = 0
    hot_topic: bool = False
    is_deleted: bool = False
    published_at: Optional[datetime] = None

    class Settings:
        name = "articles"
        indexes = [
            [("title", "text"), ("content", "text"), ("summary", "text")]
        ]


# view counts, comments, shares can be added later


class ArticleLikeModel(Document):
    article_id: Link["ArticleModel"]
    user_id: Link["UserModel"]
    created_at: datetime = Field(default_factory=datetime.now)

    
    class Settings:
        name = "article_likes"
        indexes = [
            [("article_id", 1), ("user_id", 1)]
        ]

