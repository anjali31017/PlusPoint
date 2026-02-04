from datetime import datetime, timedelta
from typing import List, Optional
from bson import ObjectId
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query

# from app.controller.user_controller import UserController
from app.controller.token_controller import get_current_user
from fastapi import status
from app.models.firm import FirmModel
from app.models.article import ArticleModel
from app.schema.dashboard_schema import ArticlePerformanceSchema, DashboardSummarySchema, EngagementTrendSchema, FirmPerformanceSchema


router = APIRouter(prefix="/dashboard", tags=["Firm"])

@router.get("/summary", response_model=DashboardSummarySchema)
async def get_dashboard_summary(
    current_user: dict = Depends(get_current_user),
):
    try:
        user_id = ObjectId(current_user["user_id"])

        # ✅ Correct Link equality query
        firms = await FirmModel.find(
            FirmModel.owner_user_id.id == user_id
        ).to_list()

        for f in firms:

            articles = await ArticleModel.find(
                ArticleModel.firm_id.id == f.id
            ).to_list()

        return DashboardSummarySchema(
            total_firms=len(firms),
            verified_firms=sum(1 for f in firms if f.is_verified),
            active_firms=sum(1 for f in firms if f.is_active),
            total_followers=sum(f.follow_count for f in firms),
            total_firm_endorsements=sum(f.endorse_count for f in firms),
            total_firm_reports=sum(f.report_count for f in firms),
            total_articles=len(articles),
            published_articles=sum(1 for a in articles if a.status == "PUBLISHED"),
            draft_articles=sum(1 for a in articles if a.status == "DRAFT"),
            pending_articles=sum(1 for a in articles if a.status == "PENDING_REVIEW"),
            rejected_articles=sum(1 for a in articles if a.status == "REJECTED"),
            total_article_likes=sum(a.like_count for a in articles),
            total_article_endorsements=sum(a.endorse_count for a in articles),
            total_article_reports=sum(a.report_count for a in articles),
            hot_topic_articles=sum(1 for a in articles if a.hot_topic),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

@router.get("/articles", response_model=List[ArticlePerformanceSchema])
async def get_articles_performance(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    current_user: dict = Depends(get_current_user),
):
    try:
        user_id = ObjectId(current_user["user_id"])
        skip = (page - 1) * page_size

        firms = await FirmModel.find(
            FirmModel.owner_user_id == user_id
        ).to_list()

        firm_ids = [f.id for f in firms]

        articles = await ArticleModel.find(
            {"firm_id": {"$in": firm_ids}},
            fetch_links=True,
        ).sort("-published_at").skip(skip).limit(page_size).to_list()

        return [
            ArticlePerformanceSchema(
                article_id=str(article.id),
                title=article.title,
                firm_name=article.firm_id.firm_name,
                status=article.status.value,
                likes=article.like_count,
                endorsements=article.endorse_count,
                reports=article.report_count,
                published_at=article.published_at,
            )
            for article in articles
        ]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

# @router.get("/firms", response_model=List[FirmPerformanceSchema])
# async def get_firms_performance(
#     page: int = Query(1, ge=1),
#     page_size: int = Query(10, ge=1, le=50),
#     current_user: dict = Depends(get_current_user),
# ):
#     try:
#         user_id = ObjectId(current_user["user_id"])
#         skip = (page - 1) * page_size

#         firms = await FirmModel.find(
#             FirmModel.owner_user_id == user_id
#         ).sort("-created_at").skip(skip).limit(page_size).to_list()

#         result = []

#         for firm in firms:
#             articles = await ArticleModel.find(
#                 {"firm_id": firm.id}
#             ).to_list()

#             result.append(
#                 FirmPerformanceSchema(
#                     firm_id=str(firm.id),
#                     firm_name=firm.firm_name,
#                     verification_status=firm.verification_status.value,
#                     followers=firm.follow_count,
#                     total_articles=len(articles),
#                     total_endorsements=sum(a.endorse_count for a in articles),
#                     total_reports=sum(a.report_count for a in articles),
#                     trust_factor=firm.trust_factor,
#                 )
#             )

#         return result

#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=str(e),
#         )

@router.get("/trends", response_model=List[EngagementTrendSchema])
async def get_engagement_trends(
    days: int = Query(30, ge=1),
    current_user: dict = Depends(get_current_user),
):
    user_id = ObjectId(current_user["user_id"])

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    firms = await FirmModel.find(
        FirmModel.owner_user_id == user_id
    ).to_list()

    firm_ids = [f.id for f in firms]

    articles = await ArticleModel.find(
        {
            "firm_id": {"$in": firm_ids},
            "published_at": {"$gte": start_date},
        }
    ).to_list()

    trends = []

    for day in range(days + 1):
        current_day = start_date + timedelta(days=day)
        next_day = current_day + timedelta(days=1)

        day_articles = [
            a for a in articles
            if a.published_at and current_day <= a.published_at < next_day
        ]

        trends.append(
            EngagementTrendSchema(
                date=current_day.strftime("%Y-%m-%d"),
                likes=sum(a.like_count for a in day_articles),
                endorsements=sum(a.endorse_count for a in day_articles),
                reports=sum(a.report_count for a in day_articles),
            )
        )

    return trends










@router.get("/firms", response_model=List[FirmPerformanceSchema])
async def get_firms_performance(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    current_user: dict = Depends(get_current_user),
):
    try:
        user_id = ObjectId(current_user["user_id"])
        skip = (page - 1) * page_size
        
        firms = await FirmModel.find(FirmModel.owner_user_id == user_id)\
            .sort("-created_at").skip(skip).limit(page_size).to_list()
        
        result = []
        for firm in firms:
            # Count total articles
            articles_count = await ArticleModel.find(ArticleModel.firm_id.id == firm.id).count()
            # Count total endorsements & reports for all articles in the firm
            articles = await ArticleModel.find(ArticleModel.firm_id.id == firm.id).to_list()
            total_endorsements = sum(a.endorse_count for a in articles)
            total_reports = sum(a.report_count for a in articles)
            
            result.append(
                FirmPerformanceSchema(
                    firm_id=str(firm.id),
                    firm_name=firm.firm_name,
                    verification_status=firm.verification_status.value,
                    followers=firm.follow_count,
                    total_articles=articles_count,
                    total_endorsements=total_endorsements,
                    total_reports=total_reports,
                    trust_factor=firm.trust_factor
                )
            )
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
