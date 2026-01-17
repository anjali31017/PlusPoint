from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional

from app.models.article import ArticleStatus

# Pydantic model for input validation
class ArticleCreateSchema(BaseModel):
    firm_username: str  # Firm ID
    title: str
    content: str
    status: ArticleStatus = ArticleStatus.DRAFT
    category: List[str] = []
    tags: List[str] = []
    hot_topic: bool = False
    
class CreateCommentSchema(BaseModel):
    content: str
    parent_comment_id: str | None = None
    
    
    

class ArticleSearchSchema(BaseModel):
    search_text: Optional[str] = None  # Single input for keyword, publisher, firm
    tags: Optional[List[str]] = []
    categories: Optional[List[str]] = []
    hot_topic: Optional[bool] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)

# class ArticleSearchSchema(BaseModel):
#     publisher_name: Optional[str] = None
#     firm_name: Optional[str] = None
#     keyword: Optional[str] = None  # search in title, content, summary
#     categories: Optional[List[str]] = None
#     tags: Optional[List[str]] = None
#     hot_topic: Optional[bool] = None
#     skip: int = 0
#     limit: int = 20

# class ArticleSearchSchema(BaseModel):
#     publisher_name: Optional[str] = None
#     firm_name: Optional[str] = None
#     keywords: Optional[List[str]] = None
#     tags: Optional[List[str]] = None
#     content_words: Optional[List[str]] = None
#     categories: Optional[List[str]] = None
#     hot_topic: Optional[bool] = None

#     start_date: Optional[datetime] = None
#     end_date: Optional[datetime] = None
#     sort_by: Optional[str] = Field(default="newest", pattern="^(newest|oldest|most_liked)$")

#     page: int = Field(default=1, ge=1)
#     page_size: int = Field(default=10, ge=1, le=100)


    
    

# class ArticleSearchResult(BaseModel):
#     id: str
#     title: str
#     content: str
#     publisher: dict
#     firm: dict
#     tags: List[str]
#     categories: List[str]
#     like_count: int
#     hot_topic: bool
#     published_at: datetime

# class ArticleSearchResponse(BaseModel):
#     total: int
#     page: int
#     page_size: int
#     results: List[ArticleSearchResult]