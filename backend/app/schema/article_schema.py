from pydantic import BaseModel
from typing import List

# Pydantic model for input validation
class ArticleCreateSchema(BaseModel):
    firm_username: str  # Firm ID
    title: str
    content: str
    category: List[str] = []
    tags: List[str] = []
    hot_topic: bool = False
    
class CreateCommentSchema(BaseModel):
    content: str
    parent_comment_id: str | None = None