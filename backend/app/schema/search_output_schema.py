from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class PublisherResult(BaseModel):
    id: str
    username: str
    first_name: Optional[str]
    last_name: Optional[str]
    profile_picture_url: Optional[str]
    articles_count: int

class FirmResult(BaseModel):
    id: str
    firm_name: str
    firm_username: str
    bio: Optional[str]
    articles_count: int

class QuickTakeResult(BaseModel):
    id: str
    title: str
    summary: Optional[str]
    publisher: PublisherResult
    firm: FirmResult
    tags: List[str]
    categories: List[str]
    published_at: datetime

class CoverageResult(BaseModel):
    id: str
    title: str
    content: str
    publisher: PublisherResult
    firm: FirmResult
    tags: List[str]
    categories: List[str]
    published_at: datetime

class MultiSectionSearchResponse(BaseModel):
    publishers: List[PublisherResult]
    firms: List[FirmResult]
    quick_take: List[QuickTakeResult]
    coverage: List[CoverageResult]
    total_counts: dict