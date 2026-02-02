from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from app.schema.article_schema import ArticleFirmOutSchema, ArticleOutSchema

# class PublisherSchema(BaseModel):
#     publisher_user_id: str

class FirmCreateSchema(BaseModel):
    firm_name: str
    # publishers: Optional[List[PublisherSchema]] = None
    bio: Optional[str] = None

class AddPublisherSchema(BaseModel):
    firm_id: str
    publisher_id: str 
    
class FirmSchema(BaseModel):
    firm_username: str
    firm_name: str
    # publishers: List[PublisherSchema] = []
    bio: Optional[str] = None
    verification_status: Optional[str] = None
    trust_factor: Optional[float] = None
    violations_count: Optional[int] = None
    created_at: datetime
    
    
class FirmDetailsOutSchema(BaseModel):
    id: str
    following: bool
    endorsed: bool
    firm_name: str
    firm_username: str
    bio: Optional[str]
    verification_status: str
    trust_factor: float
    violations_count: int
    follow_count: int
    is_verified: bool
    created_at: datetime
    owner: dict  # minimal owner info
    articles: List[ArticleFirmOutSchema]
    is_self: bool  # tag for FE