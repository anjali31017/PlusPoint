import asyncio
from datetime import datetime
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException 
from app.controller.token_controller import get_current_user
from app.schema.base_schema import BaseResponse
from app.controller.article_controller import ArticleController
from app.schema.article_schema import ArticleCreateSchema, ArticleSearchSchema, CreateCommentSchema
from app.kafka.producer import send_kafka_event
from app.celery.summary_tasks import summerization_task
from fastapi import status

from app.models.article import ArticleModel, ArticleStatus
from app.models.firm import FirmModel
from app.models.users import UserModel
from app.schema.search_output_schema import MultiSectionSearchResponse
from app.models.publisher import PublisherModel

router = APIRouter(prefix="/article", tags=["Article"])

article_controller = ArticleController()

# @router.post("/create", response_model=BaseResponse)
# async def add_article(article_data: ArticleCreateSchema, current_user: dict = Depends(get_current_user)):
#     """
#      Create article
#      Always save as DRAFT
#     """
#     try:
#         if current_user is None:
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token, Login to continue")
#         article_data_dict = article_data.dict()

#         article = await article_controller.create_article(
#             article_data_dict, 
#             current_user["user_id"]
            
#         )

#         if article is None:
#             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create article")

        
#         summary_reponse = summerization_task.delay(article.content, str(article.id))

#         return {
#             "status": 1,
#             "message": "Article created successfully",
#             "data": {
#                 "article_id":str(article.id),
#             }
#         }

#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))





@router.post("/create", response_model=BaseResponse)
async def add_article(article_data: ArticleCreateSchema, current_user: dict = Depends(get_current_user)):
# async def add_article(article_data: ArticleCreateSchema):

    try:
        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token, Login to continue")
        article_data_dict = article_data.dict()

        article = await article_controller.create_article(
            article_data_dict, 
            current_user["user_id"]
            # "692051620cbaa9500904c22d"
        )

        if article is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create article")
        # article_notification_manager.send_personal_message("hello", "692052180cbaa9500904c230")
        
        if article.status == "DRAFT":
            return {
                "status": 1,
                "message": "Article created as draft successfully",
                "data": {
                    "article_id":str(article.id),
                }
            }
        if article.status == "PENDING_REVIEW":
            raise HTTPException(status_code=status.HTTP_202_ACCEPTED, detail="Article sent for moderation")

        # final, clean Kafka event
        kafka_article_event = {
            "event_type": "article.published",
            "firm_id": str(article.firm_id.id),
            "publisher_id": current_user["user_id"],
            "article_id": str(article.id),
            "article_title": article.title,
            "firm_username": article.firm_id.firm_username,
            "publisher_username": current_user["username"],
            "published_at": (
                article.published_at.isoformat() 
                if article.published_at else datetime.now().isoformat()
            )
        }
        
        # publish event
        event  = await send_kafka_event("article.published", kafka_article_event)
        
        if event is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to send Kafka event")
        
        
        summary_reponse = summerization_task.delay(article.content, str(article.id))

        return {
            "status": 1,
            "message": "Article created successfully",
            "data": {
                "article_id":str(article.id),
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# @router.post("/publish/{article_id}", response_model=BaseResponse)
# async def publish_article(article_id: str, current_user: dict = Depends(get_current_user)):

#     try:
#         if current_user is None:
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token, Login to continue")
        
#         article = await ArticleModel.get(ObjectId(article_id))

#         if not article or article.is_deleted:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

#         publisher = await PublisherModel.find_one(
#             PublisherModel.publisher_id.id == ObjectId(current_user["user_id"]),
#             PublisherModel.firm_id.id == article.firm_id.id
#         )
#         if not publisher:
#             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

#         trust_score = publisher.trust_factor
#         article.trust_score_snapshot = trust_score
    
#         if trust_score < 40:
#             article.status = ArticleStatus.PENDING_REVIEW
#             article.moderation_required = True
#             await article.save()

#             await send_kafka_event(
#                 "moderation.requested",
#                 {
#                     "article_id": str(article.id),
#                     "publisher_id": current_user["user_id"],
#                     "firm_id": str(article.firm_id.id),
#                     "trust_score": trust_score,
#                     "trigger": "pre_publish"
#                 }
#             )
#             return {
#                 "status": 1,
#                 "message": "Article sent for moderation (pre-publish)",
#                 "data": {"article_id": str(article.id)}
#             }
        
#         # MEDIUM / HIGH TRUST → PUBLISH + POST MODERATION
#         article.status = ArticleStatus.PUBLISHED
#         article.published_at = datetime.now()
#         article.moderation_required = True
#         await article.save()
    
#         # final, clean Kafka event
#         # kafka_article_event = {
#         #     "event_type": "article_published",
#         #     "firm_id": str(article.firm_id.id),
#         #     "publisher_id": current_user["user_id"],
#         #     "article_id": str(article.id),
#         #     "article_title": article.title,
#         #     "firm_username": article.firm_id.firm_username,
#         #     "publisher_username": current_user["username"],
#         #     "published_at": (
#         #         article.published_at.isoformat() 
#         #         if article.published_at else datetime.now().isoformat()
#         #     )
#         # }
        
#         # Kafka: article published
#         await send_kafka_event(
#             "article.published",
#             {
#                 "article_id": str(article.id),
#                 "firm_id": str(article.firm_id.id),
#                 "publisher_id": current_user["user_id"],
#                 "published_at": article.published_at.isoformat()
#             }
#         )

#         # Kafka: post-publish moderation
#         await send_kafka_event(
#             "moderation.requested",
#             {
#                 "article_id": str(article.id),
#                 "publisher_id": current_user["user_id"],
#                 "firm_id": str(article.firm_id.id),
#                 "trust_score": trust_score,
#                 "trigger": "post_publish"
#             }
#         )
    
        

#         return {
#             "status": 1,
#             "message": "Article published successfully",
#             "data": {"article_id": str(article.id)}
#         }

#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



# @router.post("/create", response_model=BaseResponse)
# async def add_article(article_data: ArticleCreateSchema, current_user: dict = Depends(get_current_user)):
# # async def add_article(article_data: ArticleCreateSchema):
#     """
#      Create article
#      Always save as DRAFT
#     """
#     try:
#         if current_user is None:
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token, Login to continue")
#         article_data_dict = article_data.dict()

#         article = await article_controller.create_article(
#             article_data_dict, 
#             current_user["user_id"]
#             # "692051620cbaa9500904c22d"
#         )

#         if article is None:
#             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create article")
        # article_notification_manager.send_personal_message("hello", "692052180cbaa9500904c230")
        
        # if article.status != "published":
        #     return {
        #         "status": 1,
        #         "message": "Article created as draft successfully",
        #         "data": {
        #             "article_id":str(article.id),
        #         }
        #     }
        # # final, clean Kafka event
        # kafka_article_event = {
        #     "event_type": "article_published",
        #     "firm_id": str(article.firm_id.id),
        #     "publisher_id": current_user["user_id"],
        #     "article_id": str(article.id),
        #     "article_title": article.title,
        #     "firm_username": article.firm_id.firm_username,
        #     "publisher_username": current_user["username"],
        #     "published_at": (
        #         article.published_at.isoformat() 
        #         if article.published_at else datetime.now().isoformat()
        #     )
        # }
        
        # # publish event
        # event  = await send_kafka_event("article_published", kafka_article_event)
        
        # if event is None:
        #     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to send Kafka event")
        
        
    #     summary_reponse = summerization_task.delay(article.content, str(article.id))

    #     return {
    #         "status": 1,
    #         "message": "Article created successfully",
    #         "data": {
    #             "article_id":str(article.id),
    #         }
    #     }

    # except HTTPException:
    #     raise
    # except Exception as e:
    #     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))





@router.post("/comment", response_model=BaseResponse)
async def add_comment(
    comment_data: CreateCommentSchema, 
    article_id: str | None = None, 
    comment_id: str | None = None,
    current_user: dict = Depends(get_current_user)):
    try:
        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token, Login to continue")
        
        comment_data_dict = comment_data.dict()

        comment = await article_controller.create_comment(
            comment_data_dict, 
            article_id, 
            comment_id,
            current_user["user_id"])
        
        if comment is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create comment")
        response_data = {
            "status": 1,
            "message": "Comment added successfully",
            "data": comment
            #{
                # "comment_id": str(comment["id"]),
                # "article_id": str(comment.article_id.id),
                # "parent_comment_id": str(comment.parent_comment_id) if comment.parent_comment_id else None,
                # "content": comment.content,
                # "posted_at": comment.posted_at
            # }
        }
        return response_data

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@router.post("/like", response_model=BaseResponse)
async def like_article(article_id: str, current_user: dict = Depends(get_current_user)):
    try:
        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token, Login to continue")
        
        success = await article_controller.like_article(article_id, current_user["user_id"])
        
        if not success:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to like article")
        response_data = {
            "status": 1,
            "message": "Article liked successfully",
            "data": success
        }
        return response_data

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
    





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
            matched_publishers = await UserModel.find({
                "$or": [
                    {"username": {"$regex": text, "$options": "i"}},
                    {"first_name": {"$regex": text, "$options": "i"}},
                    {"last_name": {"$regex": text, "$options": "i"}},
                ]
            }).to_list()

            for p in matched_publishers:
                article_count = await ArticleModel.find({"publisher_id": p.id}).count()
                publisher_results.append({
                    "id": str(p.id),
                    "username": p.username,
                    "first_name": p.first_name,
                    "last_name": p.last_name,
                    "profile_picture_url": p.profile_picture_url,
                    "articles_count": article_count
                })

        # -------------------
        # Firms Section
        # -------------------
        firm_results = []
        if text:  # only search if text is not empty
            matched_firms = await FirmModel.find({"firm_name": {"$regex": text, "$options": "i"}}).to_list()
            for f in matched_firms:
                article_count = await ArticleModel.find({"firm_id": f.id}).count()
                firm_results.append({
                    "id": str(f.id),
                    "firm_name": f.firm_name,
                    "firm_username": f.firm_username,
                    "bio": f.bio,
                    "articles_count": article_count
                })


        # # -------------------
        # # Publishers Section
        # # -------------------
        # matched_publishers = await UserModel.find({
        #     "$or": [
        #         {"username": {"$regex": text, "$options": "i"}},
        #         {"first_name": {"$regex": text, "$options": "i"}},
        #         {"last_name": {"$regex": text, "$options": "i"}},
        #     ]
        # }).to_list()

        # publisher_results = []
        # for p in matched_publishers:
        #     article_count = await ArticleModel.find({"publisher_id": p.id}).count()
        #     publisher_results.append({
        #         "id": str(p.id),
        #         "username": p.username,
        #         "first_name": p.first_name,
        #         "last_name": p.last_name,
        #         "profile_picture_url": p.profile_picture_url,
        #         "articles_count": article_count
        #     })

        # # -------------------
        # # Firms Section
        # # -------------------
        # matched_firms = await FirmModel.find({"firm_name": {"$regex": text, "$options": "i"}}).to_list()
        # firm_results = []
        # for f in matched_firms:
        #     article_count = await ArticleModel.find({"firm_id": f.id}).count()
        #     firm_results.append({
        #         "id": str(f.id),
        #         "firm_name": f.firm_name,
        #         "firm_username": f.firm_username,
        #         "bio": f.bio,
        #         "articles_count": article_count
        #     })

        # -------------------
        # Articles Section (QuickTake & Coverage)
        # -------------------
        # article_filters = {"$or": [
        #     {"title": {"$regex": text, "$options": "i"}},
        #     {"summary": {"$regex": text, "$options": "i"}},
        #     {"content": {"$regex": text, "$options": "i"}},
        #     {"tags": text},  # simple tag match
        # ]} if text else {}

        # if search.tags:
        #     article_filters["tags"] = {"$in": search.tags}
        # if search.categories:
        #     article_filters["category"] = {"$in": search.categories}
        # if search.hot_topic is not None:
        #     article_filters["hot_topic"] = search.hot_topic

        # article_filters = {}

        # # Text search
        # if search.search_text:
        #     text = search.search_text
        #     article_filters["$or"] = [
        #         {"title": {"$regex": text, "$options": "i"}},
        #         {"summary": {"$regex": text, "$options": "i"}},
        #         {"content": {"$regex": text, "$options": "i"}},
        #         {"tags": text},  # simple match
        #     ]

        # # Tags filter
        # if search.tags:
        #     article_filters["tags"] = {"$in": search.tags}

        # # Categories filter
        # if search.categories:
        #     article_filters["category"] = {"$in": search.categories}

        # # Hot topic filter
        # if search.hot_topic is not None:
        #     article_filters["hot_topic"] = search.hot_topic
        
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
            article_filters["hot_topic"] = search.hot_topic
    
        skip = (page - 1) * page_size
        articles = await ArticleModel.find(article_filters).sort("-published_at").skip(skip).limit(page_size).to_list()

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
                "articles_count": await ArticleModel.find({"publisher_id": publisher.id}).count()
            }

            firm_obj = {
                "id": str(firm.id),
                "firm_name": firm.firm_name,
                "firm_username": firm.firm_username,
                "bio": firm.bio,
                "articles_count": await ArticleModel.find({"firm_id": firm.id}).count()
            }

            # QuickTake = summary
            if a.summary:
                quick_take_results.append({
                    "id": str(a.id),
                    "title": a.title,
                    "summary": a.summary,
                    "publisher": publisher_obj,
                    "firm": firm_obj,
                    "tags": a.tags,
                    "categories": a.category,
                    "published_at": a.published_at
                })

            # Coverage = full content
            coverage_results.append({
                "id": str(a.id),
                "title": a.title,
                "content": a.content,
                "publisher": publisher_obj,
                "firm": firm_obj,
                "tags": a.tags,
                "categories": a.category,
                "published_at": a.published_at
            })

        return {
            "publishers": publisher_results,
            "firms": firm_results,
            "quick_take": quick_take_results,
            "coverage": coverage_results,
            "total_counts": {
                "publishers": len(publisher_results),
                "firms": len(firm_results),
                "quick_take": len(quick_take_results),
                "coverage": len(coverage_results)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
# @router.post("/search", response_model=ArticleSearchResponse, status_code=status.HTTP_200_OK)
# async def search_articles(search: ArticleSearchSchema):
#     data = await article_controller.search_articles(
#         publisher_name=search.publisher_name,
#         firm_name=search.firm_name,
#         keywords=search.keywords,
#         tags=search.tags,
#         content_words=search.content_words,
#         categories=search.categories,
#         hot_topic=search.hot_topic,
#         page=search.page,
#         page_size=search.page_size
#     )
#     try:
#         # Build response with publisher and firm details
#         results = []
#         for a in data["articles"]:
#             publisher = await a.publisher_id.fetch()
#             firm = await a.firm_id.fetch()
#             results.append(
#                 ArticleSearchResult(
#                     id=str(a.id),
#                     title=a.title,
#                     content=a.content,
#                     publisher={
#                         "id": str(publisher.id),
#                         "username": publisher.username,
#                         "first_name": publisher.first_name,
#                         "last_name": publisher.last_name,
#                     },
#                     firm={
#                         "id": str(firm.id),
#                         "firm_name": getattr(firm, "firm_name", ""),
#                     },
#                     tags=a.tags,
#                     categories=a.category,
#                     like_count=a.like_count,
#                     hot_topic=a.hot_topic,
#                     published_at=a.published_at
#                 )
#             )

#         return ArticleSearchResponse(
#             total=data["total"],
#             page=search.page,
#             page_size=search.page_size,
#             results=results
#         )
#     except Exception as e:  
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
# @router.post("/search", response_model=BaseResponse)
# async def search_articles_api(search_data: ArticleSearchSchema, current_user: dict = Depends(get_current_user)):
#     """
#     Search articles based on publisher, firm, keyword, category, tags, hot_topic.
#     """
#     if current_user is None:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token, Login to continue")

#     try:
#         articles = await article_controller.search_articles(search_data)
#         if articles is None:
#             return BaseResponse(status=1, message="No articles found", data=[])
#         return BaseResponse(
#             status=1,
#             message=f"{len(articles)} articles found",
#             data=[article.dict() for article in articles]
#         )
#     except Exception as e:
#         return BaseResponse(status=0, message=f"Internal server error: {str(e)}", data=None)