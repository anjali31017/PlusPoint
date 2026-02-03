import asyncio
from datetime import datetime
import os
import shutil
import uuid
from bson import ObjectId
from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, Query, UploadFile
from app.controller.token_controller import get_current_user
from app.schema.base_schema import BaseResponse
from app.controller.article_controller import ArticleController
from app.schema.article_schema import (
    ArticleCreateSchema,
    ArticleFirmOutSchema,
    ArticleSearchSchema,
    CreateCommentSchema,
)
from app.kafka.producer import send_kafka_event
from app.celery.summary_tasks import summerization_task
from fastapi import status

from app.models.article import ArticleModel, ArticleStatus
from app.models.firm import FirmModel
from app.models.users import UserModel
from app.schema.search_output_schema import MultiSectionSearchResponse
from app.config import settings

router = APIRouter(prefix="/article", tags=["Article"])

article_controller = ArticleController()


@router.post("/create", response_model=BaseResponse)
async def add_article(
    article_data: ArticleCreateSchema,
    background_tasks: BackgroundTasks,
    firm_id: str = Query(None),
    # cover_page: UploadFile | None = File(None),
    current_user: dict = Depends(get_current_user),
):
    # async def add_article(article_data: ArticleCreateSchema):

    try:
        if current_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid access token, Login to continue",
            )
        article_data_dict = article_data.dict()
            
        article = await article_controller.create_article(
            firm_id,
            article_data_dict,
            current_user["user_id"],
            # "692051620cbaa9500904c22d"
        )

        if article is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create article",
            )

        if article.status == "DRAFT":
            return {
                "status": 1,
                "message": "Article created as draft successfully",
                "data": {
                    "article_id": str(article.id),
                },
            }
        if article.status == "PENDING_REVIEW":
            raise HTTPException(
                status_code=status.HTTP_202_ACCEPTED,
                detail="Article sent for moderation",
            )

        # final, clean Kafka event
        kafka_article_event = {
            "event_type": "article.published",
            "firm_id": str(article.firm_id.id),
            "article_id": str(article.id),
            "article_title": article.title,
            "firm_username": article.firm_id.firm_username,
            "published_at": (
                article.published_at.isoformat()
                if article.published_at
                else datetime.now().isoformat()
            ),
        }
        
        background_tasks.add_task(
            send_kafka_event,
            "article.published", 
            kafka_article_event
        )

        
        summary_reponse = summerization_task.delay(article.content, str(article.id))

        return {
            "status": 1,
            "message": "Article created successfully",
            "data": {
                "article_id": str(article.id),
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/media/upload", response_model=BaseResponse)
async def upload_media(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    try:
        if not file:
            raise HTTPException(
                status_code=400,
                detail="File Not Found"
            )

        # Extract original file extension
        ext = os.path.splitext(file.filename)[1]  # .jpg, .mp4, etc.

        # Generate a unique filename using uuid
        unique_filename = f"{uuid.uuid4().hex}{ext}"

        # Ensure upload directory exists
        os.makedirs(settings.TINYMCE_UPLOAD_FOLDER, exist_ok=True)

        # Save file
        filepath = os.path.join(settings.TINYMCE_UPLOAD_FOLDER, unique_filename)
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Return the public URL
        file_url = f"http://127.0.0.1:3000/src/images/articles/{unique_filename}"

        return {
            "status": 1,
            "message": "Media uploaded successfully",
            "data": {
                "location": file_url,
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

    
    

@router.post("/comment", response_model=BaseResponse)
async def add_comment(
    comment_data: CreateCommentSchema,
    article_id: str | None = None,
    comment_id: str | None = None,
    current_user: dict = Depends(get_current_user),
):
    try:
        if current_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid access token, Login to continue",
            )

        comment_data_dict = comment_data.dict()

        comment = await article_controller.create_comment(
            comment_data_dict, article_id, comment_id, current_user["user_id"]
        )

        if comment is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create comment",
            )
        response_data = {
            "status": 1,
            "message": "Comment added successfully",
            "data": comment,

        }
        return response_data

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/like", response_model=BaseResponse)
async def like_article(
    background_tasks: BackgroundTasks,
    article_id: str = Query(None),
    current_user: dict = Depends(get_current_user),
):
    try:
        if current_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid access token, Login to continue",
            )

        success = await article_controller.like_article(
            article_id, current_user["user_id"]
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to like article",
            )

        if success["status"] == "liked":
            background_tasks.add_task(
                send_kafka_event,  # function itself, no parentheses
                "article.like",  # first argument
                success["data"],  # second argument
            )

        response_data = {
            "status": 1,
            "message": (
                "Article unliked"
                if success["status"] == "un-liked" else "Article liked"
            ),
            "data": success,
        }
        return response_data

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/search", response_model=MultiSectionSearchResponse)
async def search_multi_section(search: ArticleSearchSchema):
    try:
        text = search.search_text or ""
        page = search.page
        page_size = search.page_size

        # -------------------
        # Publishers Section
        # -------------------
        publisher_results = []
        if text:  # only search if text is not empty
            matched_publishers = await UserModel.find(
                {
                    "$or": [
                        {"username": {"$regex": text, "$options": "i"}},
                        {"first_name": {"$regex": text, "$options": "i"}},
                        {"last_name": {"$regex": text, "$options": "i"}},
                    ]
                }
            ).to_list()

            for p in matched_publishers:
                article_count = await ArticleModel.find({"publisher_id": p.id}).count()
                publisher_results.append(
                    {
                        "id": str(p.id),
                        "username": p.username,
                        "first_name": p.first_name,
                        "last_name": p.last_name,
                        "profile_picture_url": p.profile_picture_url,
                        "articles_count": article_count,
                    }
                )

        # -------------------
        # Firms Section
        # -------------------
        firm_results = []
        if text:  # only search if text is not empty
            matched_firms = await FirmModel.find(
                {"firm_name": {"$regex": text, "$options": "i"}}
            ).to_list()
            for f in matched_firms:
                article_count = await ArticleModel.find({"firm_id": f.id}).count()
                firm_results.append(
                    {
                        "id": str(f.id),
                        "firm_name": f.firm_name,
                        "firm_username": f.firm_username,
                        "bio": f.bio,
                        "articles_count": article_count,
                    }
                )

        article_filters = {}

        # Text search (title, summary, content)
        if search.search_text:
            text = search.search_text
            article_filters["$or"] = [
                {"title": {"$regex": text, "$options": "i"}},
                {"summary": {"$regex": text, "$options": "i"}},
                {"content": {"$regex": text, "$options": "i"}},
                {"tags": {"$regex": text, "$options": "i"}},  # match tags as string
            ]

        # Tags filter (case-insensitive)
        if search.tags:
            # match any tag in search.tags, ignoring case
            article_filters["tags"] = {
                "$elemMatch": {"$regex": "|".join(search.tags), "$options": "i"}
            }

        # Categories filter (case-insensitive)
        if search.categories:
            article_filters["category"] = {
                "$elemMatch": {"$regex": "|".join(search.categories), "$options": "i"}
            }

        # Hot topic filter
        if search.hot_topic is not None:
            article_filters["hot_topic"] = True

        article_filters["moderation_required"] = False
        article_filters["status"] = ArticleStatus.PUBLISHED
        skip = (page - 1) * page_size
        articles = (
            await ArticleModel.find(article_filters)
            .sort("-published_at")
            .skip(skip)
            .limit(page_size)
            .to_list()
        )

        quick_take_results = []
        coverage_results = []
        for a in articles:
            publisher = await a.publisher_id.fetch()
            firm = await a.firm_id.fetch()

            publisher_obj = {
                "id": str(publisher.id),
                "username": publisher.username,
                "first_name": publisher.first_name,
                "last_name": publisher.last_name,
                "profile_picture_url": publisher.profile_picture_url,
                "articles_count": await ArticleModel.find(
                    {"publisher_id": publisher.id}
                ).count(),
            }

            firm_obj = {
                "id": str(firm.id),
                "firm_name": firm.firm_name,
                "firm_username": firm.firm_username,
                "bio": firm.bio,
                "articles_count": await ArticleModel.find({"firm_id": firm.id}).count(),
            }

            # QuickTake = summary
            if a.summary:
                quick_take_results.append(
                    {
                        "id": str(a.id),
                        "title": a.title,
                        "summary": a.summary,
                        "publisher": publisher_obj,
                        "firm": firm_obj,
                        "tags": a.tags,
                        "categories": a.category,
                        "published_at": a.published_at,
                    }
                )

            # Coverage = full content
            coverage_results.append(
                {
                    "id": str(a.id),
                    "title": a.title,
                    "content": a.content,
                    "publisher": publisher_obj,
                    "firm": firm_obj,
                    "tags": a.tags,
                    "categories": a.category,
                    "published_at": a.published_at,
                }
            )

        return {
            "publishers": publisher_results,
            "firms": firm_results,
            "quick_take": quick_take_results,
            "coverage": coverage_results,
            "total_counts": {
                "publishers": len(publisher_results),
                "firms": len(firm_results),
                "quick_take": len(quick_take_results),
                "coverage": len(coverage_results),
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )




@router.get("/detail", response_model=BaseResponse)
async def get_single_article(
    article_id: str = Query(...),
    current_user: dict = Depends(get_current_user)
):
    try:
        if current_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid access token, Login to continue",
            )
        
        article_data = await article_controller.get_article_by_id(article_id, current_user)
        if article_data is None:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )
        return {
            "status": 1,
            "message": "Article fetched successfully",
            "data": article_data.dict()
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )




@router.get("/coverage", response_model=BaseResponse)
async def get_firm_details(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    current_user: dict = Depends(get_current_user)
):
    try:
        if current_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid access token, Login to continue",
            )
        
        # Pagination
        skip = (page - 1) * page_size

        # Fetch published articles
        articles_cursor = ArticleModel.find(
            ArticleModel.status == "PUBLISHED",
            ArticleModel.is_deleted == False
        ).sort("-published_at").skip(skip).limit(page_size)

        # print(articles_cursor)
        articles = []
        
        async for article in articles_cursor:

            article_data = {
                "id":str(article.id),
                "title":article.title,
                "summary":article.summary,
                "tags":article.tags,
                "category":article.category,
                "like_count": article.like_count,
                "published_at": article.published_at
            }
            articles.append(article_data)
        
        return{
            "status": 1,
            "message": "Firm fetched successfully",
            "data": articles
        } 
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
        