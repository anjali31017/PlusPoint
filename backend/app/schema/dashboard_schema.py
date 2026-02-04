from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class ArticlePerformanceSchema(BaseModel):
    article_id: str
    title: str
    firm_name: str
    status: str
    likes: int
    endorsements: int
    reports: int
    published_at: Optional[datetime]

class FirmPerformanceSchema(BaseModel):
    firm_id: str
    firm_name: str
    verification_status: str
    followers: int
    total_articles: int
    total_endorsements: int
    total_reports: int
    trust_factor: float

class DashboardSummarySchema(BaseModel):
    total_firms: int
    verified_firms: int
    active_firms: int
    total_followers: int
    total_firm_endorsements: int
    total_firm_reports: int
    total_articles: int
    published_articles: int
    draft_articles: int
    pending_articles: int
    rejected_articles: int
    total_article_likes: int
    total_article_endorsements: int
    total_article_reports: int
    hot_topic_articles: int

class DashboardResponseSchema(BaseModel):
    summary: DashboardSummarySchema
    articles: List[ArticlePerformanceSchema] = []
    firms: List[FirmPerformanceSchema] = []


class EngagementTrendSchema(BaseModel):
    date: str
    likes: int
    endorsements: int
    reports: int
