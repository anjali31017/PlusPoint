from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException 
from app.controller.token_controller import get_current_user
from app.schema.base_schema import BaseResponse
from app.controller.article_controller import ArticleController
from app.schema.article_schema import ArticleCreateSchema, CreateCommentSchema
from app.kafka.producer import send_kafka_event
from app.celery.summary_tasks import final_summary

router = APIRouter(prefix="/article", tags=["Article"])

article_controller = ArticleController()

@router.post("/create", response_model=BaseResponse)
# async def add_article(article_data: ArticleCreateSchema, current_user: dict = Depends(get_current_user)):
async def add_article(article_data: ArticleCreateSchema):
    try:
        article_data_dict = article_data.dict()

        article = await article_controller.create_article(
            article_data_dict, 
            # current_user["user_id"]
            "692051620cbaa9500904c22d"
        )

        if article is None:
            raise HTTPException(status_code=500, detail="Failed to create article")
        # article_notification_manager.send_personal_message("hello", "692052180cbaa9500904c230")
        
        # final, clean Kafka event
        kafka_article_event = {
            "event_type": "article_published",
            "firm_id": str(article.firm_id.id),
            "publisher_id": "692051620cbaa9500904c22d", #current_user["user_id"],
            "article_id": str(article.id),
            "article_title": article.title,
            "firm_username": article.firm_id.firm_username,
            "publisher_username": "692051620cbaa9500904c22d", #current_user["username"],
            "published_at": (
                article.published_at.isoformat() 
                if article.published_at else datetime.now().isoformat()
            )
        }
        
        # publish event
        event  = await send_kafka_event("article_published", kafka_article_event)
        
        if event is None:
            raise HTTPException(status_code=500, detail="Failed to send Kafka event")
        
        # firm_obj_id = ObjectId(str(article.firm_id.id))
        # publisher_obj_id = ObjectId(current_user["user_id"])
        # firm_subscriptions = await SubscriptionModel.find(SubscriptionModel.firm_id.id == firm_obj_id).to_list()
        # publisher_subscriptions = await SubscriptionModel.find(SubscriptionModel.publisher_id.id == publisher_obj_id).to_list()
        
        # all_subscriptions = [str(sub.subscriber_id.ref.id) for sub in firm_subscriptions] + [str(sub.subscriber_id.ref.id) for sub in publisher_subscriptions]
        # all_subscriptions = list(set(all_subscriptions))  # Remove duplicates
        # await sse_connection_manager.send_to_user("692052180cbaa9500904c230", {"msg": "Hello!"})
        
        
        # summary_reponse = multi_stage_summary.delay(article.content, article.id)
        summary_reponse = final_summary.delay(article.content, str(article.id))
        
        
        
    #     db_entry = article_controller.update_article(article.id, {
    #     "summary": summary_reponse["final_summary"]
    # })
        return {
            "status": 1,
            "message": "Article created successfully",
            "data": {
                "article_id":str(article.id),
                # "summary": summary_reponse,
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# @router.post("/create", response_model=BaseResponse)
# async def add_article(article_data: ArticleCreateSchema,  current_user: dict = Depends(get_current_user)):
#     try:
#         article_data_dict = article_data.dict()

#         article = await article_controller.create_article(article_data_dict, current_user["user_id"])
        
#         if article is None:
#             raise HTTPException(status_code=500, detail="Failed to create article")
        
#         kafka_article_event = {
#             "firm_id": str(article.firm_id.id),
#             # "publisher_id": article.publisher_id.id,
#             "publisher_id": current_user["user_id"],
#             "article_id": str(article.id),
#             "article_title": article.title,
#             "article_firm": article.firm_id.firm_username,
#             "article_publisher": current_user["username"],
#             # "published_at": article.published_at
#         }
#         await send_kafka_event("article_published",kafka_article_event )
        
#         response_data = {
#             "status": 1,
#             "message": "Article created successfully",
#             "data": {
#                 "article_id": str(article.id),
#                 # "data":article
#                 "details": kafka_article_event
#             }
#         }
#         return response_data

#     except HTTPException as he:
#         raise he
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e)) 
    
# @router.post("/{article_id}/comment/{comment_id}", response_model=BaseResponse)
# @router.post("/{article_id}/comment", response_model=BaseResponse)

@router.post("/comment", response_model=BaseResponse)
async def add_comment(
    comment_data: CreateCommentSchema, 
    article_id: str | None = None, 
    comment_id: str | None = None,
    current_user: dict = Depends(get_current_user)):
    try:
        comment_data_dict = comment_data.dict()

        comment = await article_controller.create_comment(
            comment_data_dict, 
            article_id, 
            comment_id,
            current_user["user_id"])
        
        if comment is None:
            raise HTTPException(status_code=500, detail="Failed to create comment")
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
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/like", response_model=BaseResponse)
async def like_article(article_id: str, current_user: dict = Depends(get_current_user)):
    try:
        success = await article_controller.like_article(article_id, current_user["user_id"])
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to like article")
        response_data = {
            "status": 1,
            "message": "Article liked successfully",
            "data": success
        }
        return response_data

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))