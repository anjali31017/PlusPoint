from fastapi import HTTPException
from app.models.article import ArticleModel
from app.models.firm import FirmModel
from app.models.users import UserModel
from pydantic import BaseModel
from datetime import datetime
from typing import List

# Pydantic model for input validation
class ArticleCreateSchema(BaseModel):
    firm_id: str  # Firm ID
    publisher_id: str  # Publisher ID (User ID)
    title: str
    content: str
    category: List[str] = []
    tags: List[str] = []
    hot_topic: bool = False