from datetime import datetime, timedelta
from typing import List, Optional
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.controller.token_controller import get_current_user
from app.models.firm import FirmModel
from app.models.article import ArticleModel, ArticleStatus
from app.schema.dashboard_schema import (
    ArticlePerformanceSchema,
    DashboardSummarySchema,
    EngagementTrendSchema,
    FirmPerformanceSchema
)
from beanie.operators import In, NE, GTE

router = APIRouter(prefix="/dashboard", tags=["Firm"])


# --------------------- Helper Functions --------------------- #

async def get_user_id(current_user: dict) -> ObjectId:
    """Extract ObjectId from current_user."""
    return ObjectId(current_user["user_id"])


async def get_user_firms(user_id: ObjectId) -> List[FirmModel]:
    """Fetch all firms belonging to a user."""
    return await FirmModel.find(FirmModel.owner_user_id.id == user_id).to_list()


def get_firm_ids(firms: List[FirmModel]) -> List[ObjectId]:
    """Return list of firm IDs."""
    return [f.id for f in firms]


def normalize_start_date(days: int) -> datetime:
    """Return start date normalized to midnight."""
    return (datetime.now() - timedelta(days=days)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )


async def get_articles_for_firms(firm_ids: List[ObjectId], published_only: bool = False, start_date: Optional[datetime] = None) -> List[ArticleModel]:
    """Fetch articles for given firm IDs with optional filters."""
    if not firm_ids:
        return []

    query = [In(ArticleModel.firm_id.id, firm_ids), ArticleModel.is_deleted == False]

    if published_only:
        query.append(ArticleModel.status == ArticleStatus.PUBLISHED)
    if start_date:
        query.append(NE(ArticleModel.published_at, None))
        query.append(GTE(ArticleModel.published_at, start_date))

    return await ArticleModel.find(*query).to_list()


# --------------------- Endpoints --------------------- #

@router.get("/summary", response_model=DashboardSummarySchema)
async def get_dashboard_summary(current_user: dict = Depends(get_current_user)):
    try:
        user_id = await get_user_id(current_user)
        firms = await get_user_firms(user_id)
        firm_ids = get_firm_ids(firms)
        articles = await get_articles_for_firms(firm_ids)

        return DashboardSummarySchema(
            total_firms=len(firms),
            verified_firms=sum(1 for f in firms if f.is_verified),
            active_firms=sum(1 for f in firms if f.is_active),
            total_followers=sum(f.follow_count for f in firms),
            total_firm_endorsements=sum(f.endorse_count for f in firms),
            total_firm_reports=sum(f.report_count for f in firms),
            total_articles=len(articles),
            published_articles=sum(1 for a in articles if a.status == ArticleStatus.PUBLISHED),
            pending_articles=sum(1 for a in articles if a.status == ArticleStatus.PENDING_REVIEW),
            # rejected_articles=sum(1 for a in articles if a.status == ArticleStatus.REJECTED),
            total_article_likes=sum(a.like_count for a in articles),
            total_article_endorsements=sum(a.endorse_count for a in articles),
            total_article_reports=sum(a.report_count for a in articles),
            hot_topic_articles=sum(1 for a in articles if a.hot_topic),
        )

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/articles", response_model=List[ArticlePerformanceSchema])
async def get_articles_performance(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    current_user: dict = Depends(get_current_user)
):
    try:
        user_id = await get_user_id(current_user)
        skip = (page - 1) * page_size

        firms = await get_user_firms(user_id)
        firm_ids = get_firm_ids(firms)
        if not firm_ids:
            return []

        articles = await get_articles_for_firms(firm_ids)
        articles = sorted(articles, key=lambda x: x.published_at or datetime.min, reverse=True)
        articles = articles[skip: skip + page_size]

        return [
            ArticlePerformanceSchema(
                article_id=str(a.id),
                title=a.title,
                status=a.status.value,
                likes=a.like_count,
                endorsements=a.endorse_count,
                reports=a.report_count,
                published_at=a.published_at,
            )
            for a in articles
        ]

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/trends", response_model=List[EngagementTrendSchema])
async def get_engagement_trends(
    days: int = Query(30, ge=1),
    current_user: dict = Depends(get_current_user)
):
    try:
        user_id = await get_user_id(current_user)
        start_date = normalize_start_date(days)
        firms = await get_user_firms(user_id)
        firm_ids = get_firm_ids(firms)
        if not firm_ids:
            return []

        articles = await get_articles_for_firms(firm_ids, published_only=True, start_date=start_date)

        trends = []
        for day in range(days + 1):
            current_day = start_date + timedelta(days=day)
            next_day = current_day + timedelta(days=1)
            day_articles = [a for a in articles if current_day <= a.published_at < next_day]

            trends.append(
                EngagementTrendSchema(
                    date=current_day.strftime("%Y-%m-%d"),
                    likes=sum(a.like_count for a in day_articles),
                    endorsements=sum(a.endorse_count for a in day_articles),
                    reports=sum(a.report_count for a in day_articles),
                )
            )

        return trends

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/firms", response_model=List[FirmPerformanceSchema])
async def get_firms_performance(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    current_user: dict = Depends(get_current_user)
):
    try:
        user_id = await get_user_id(current_user)
        skip = (page - 1) * page_size
        firms = await get_user_firms(user_id)
        firms = sorted(firms, key=lambda f: f.created_at, reverse=True)
        firms = firms[skip: skip + page_size]
        if not firms:
            return []

        firm_ids = get_firm_ids(firms)
        articles = await get_articles_for_firms(firm_ids)

        # Group articles by firm
        articles_by_firm = {}
        for a in articles:
            fid = a.firm_id.ref.id
            articles_by_firm.setdefault(fid, []).append(a)

        return [
            FirmPerformanceSchema(
                firm_id=str(firm.id),
                firm_name=firm.firm_name,
                verification_status=firm.verification_status.value,
                followers=firm.follow_count,
                total_articles=len(articles_by_firm.get(firm.id, [])),
                total_endorsements=sum(a.endorse_count for a in articles_by_firm.get(firm.id, [])),
                total_reports=sum(a.report_count for a in articles_by_firm.get(firm.id, [])),
                trust_factor=firm.trust_factor,
            )
            for firm in firms
        ]

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))










# from datetime import datetime, timedelta
# from typing import List, Optional
# from bson import ObjectId
# from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query

# # from app.controller.user_controller import UserController
# from app.controller.token_controller import get_current_user
# from fastapi import status
# from app.models.firm import FirmModel
# from app.models.article import ArticleModel, ArticleStatus
# from app.schema.dashboard_schema import ArticlePerformanceSchema, DashboardSummarySchema, EngagementTrendSchema, FirmPerformanceSchema
# from beanie.operators import In, NE, GTE

# router = APIRouter(prefix="/dashboard", tags=["Firm"])

# @router.get("/summary", response_model=DashboardSummarySchema)
# async def get_dashboard_summary(
#     current_user: dict = Depends(get_current_user),
# ):
#     try:
#         user_id = ObjectId(current_user["user_id"])

#         firms = await FirmModel.find(
#             FirmModel.owner_user_id.id == user_id
#         ).to_list()
        
#         firm_ids = [f.id for f in firms]

#         articles = []
#         if firm_ids:
#             articles = await ArticleModel.find(
#                 In(ArticleModel.firm_id.id, firm_ids),
#                 ArticleModel.is_deleted == False
#             ).to_list()
            

#         return DashboardSummarySchema(
#             total_firms=len(firms),
#             verified_firms=sum(1 for f in firms if f.is_verified),
#             active_firms=sum(1 for f in firms if f.is_active),
#             total_followers=sum(f.follow_count for f in firms),
#             total_firm_endorsements=sum(f.endorse_count for f in firms),
#             total_firm_reports=sum(f.report_count for f in firms),
#             total_articles=len(articles),
#             published_articles=sum(1 for a in articles if a.status == ArticleStatus.PUBLISHED),
#             # draft_articles=sum(1 for a in articles if a.status == "DRAFT"),
#             pending_articles=sum(1 for a in articles if a.status == ArticleStatus.PENDING_REVIEW),
#             rejected_articles=sum(1 for a in articles if a.status == ArticleStatus.REJECTED),
#             total_article_likes=sum(a.like_count for a in articles),
#             total_article_endorsements=sum(a.endorse_count for a in articles),
#             total_article_reports=sum(a.report_count for a in articles),
#             hot_topic_articles=sum(1 for a in articles if a.hot_topic),
#         )

#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=str(e),
#         )

# @router.get("/articles", response_model=List[ArticlePerformanceSchema])
# async def get_articles_performance(
#     page: int = Query(1, ge=1),
#     page_size: int = Query(10, ge=1, le=50),
#     current_user: dict = Depends(get_current_user),
# ):
#     try:
#         user_id = ObjectId(current_user["user_id"])
#         skip = (page - 1) * page_size

#         firms = await FirmModel.find(
#             FirmModel.owner_user_id.id == user_id
#         ).to_list()

#         firm_ids = [f.id for f in firms]

#         if not firm_ids:
#             return []
 
#         articles = await ArticleModel.find(
#             In(ArticleModel.firm_id.id, firm_ids),
#             ArticleModel.is_deleted == False,
#             # fetch_links=True,
#         ).sort("-published_at").skip(skip).limit(page_size).to_list()

#         return [
#             ArticlePerformanceSchema(
#                 article_id=str(article.id),
#                 title=article.title,
#                 # firm_name=article.firm_id.firm_name,
#                 status=article.status.value,
#                 likes=article.like_count,
#                 endorsements=article.endorse_count,
#                 reports=article.report_count,
#                 published_at=article.published_at,
#             )
#             for article in articles
#         ]

#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=str(e),
#         )


# @router.get("/trends", response_model=List[EngagementTrendSchema])
# async def get_engagement_trends(
#     days: int = Query(30, ge=1),
#     current_user: dict = Depends(get_current_user),
# ):
#     try:
#         user_id = ObjectId(current_user["user_id"])

#         # Start date normalized to midnight
#         start_date = (datetime.now() - timedelta(days=days)).replace(
#             hour=0, minute=0, second=0, microsecond=0
#         )

#         # Fetch user's firms
#         firms = await FirmModel.find(FirmModel.owner_user_id.id == user_id).to_list()
#         firm_ids = [f.id for f in firms]

#         if not firm_ids:
#             return []

#         # Fetch published, non-deleted articles for these firms
#         articles = await ArticleModel.find(
#             In(ArticleModel.firm_id.id, firm_ids),  # ✅ use .id for Link fields
#             ArticleModel.status == ArticleStatus.PUBLISHED,  # only published
#             ArticleModel.is_deleted == False,
#             NE(ArticleModel.published_at, None),
#             GTE(ArticleModel.published_at, start_date),
#         ).to_list()

#         trends = []

#         for day in range(days + 1):
#             current_day = start_date + timedelta(days=day)
#             next_day = current_day + timedelta(days=1)

#             # Filter articles published on this day
#             day_articles = [
#                 a for a in articles
#                 if current_day <= a.published_at < next_day
#             ]

#             trends.append(
#                 EngagementTrendSchema(
#                     date=current_day.strftime("%Y-%m-%d"),
#                     likes=sum(a.like_count for a in day_articles),
#                     endorsements=sum(a.endorse_count for a in day_articles),
#                     reports=sum(a.report_count for a in day_articles),
#                 )
#             )

#         return trends

#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=str(e)
#         )





# @router.get("/firms", response_model=List[FirmPerformanceSchema])
# async def get_firms_performance(
#     page: int = Query(1, ge=1),
#     page_size: int = Query(10, ge=1, le=50),
#     current_user: dict = Depends(get_current_user),
# ):
#     try:
#         user_id = ObjectId(current_user["user_id"])
#         skip = (page - 1) * page_size

#         firms = await (
#             FirmModel.find(FirmModel.owner_user_id.id == user_id)
#             .sort("-created_at")
#             .skip(skip)
#             .limit(page_size)
#             .to_list()
#         )

#         if not firms:
#             return []

#         from beanie.operators import In

#         firm_ids = [f.id for f in firms]

#         articles = await (
#             ArticleModel.find(
#                 In(ArticleModel.firm_id, firm_ids),
#                 ArticleModel.is_deleted == False
#             ).to_list()
#         )

#         articles_by_firm = {}
#         for a in articles:
#             fid = a.firm_id.ref.id   # ✅ FIX
#             articles_by_firm.setdefault(fid, []).append(a)

#         return [
#             FirmPerformanceSchema(
#                 firm_id=str(firm.id),
#                 firm_name=firm.firm_name,
#                 verification_status=firm.verification_status.value,
#                 followers=firm.follow_count,
#                 total_articles=len(articles_by_firm.get(firm.id, [])),
#                 total_endorsements=sum(
#                     a.endorse_count for a in articles_by_firm.get(firm.id, [])
#                 ),
#                 total_reports=sum(
#                     a.report_count for a in articles_by_firm.get(firm.id, [])
#                 ),
#                 trust_factor=firm.trust_factor,
#             )
#             for firm in firms
#         ]

#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=str(e),
#         )


