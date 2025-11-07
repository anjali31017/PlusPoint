from fastapi import APIRouter, Depends, HTTPException 
from app.controller.token_controller import get_current_user
from app.schema.base_schema import BaseResponse
from app.controller.article_controller import ArticleController
from app.schema.article_schema import ArticleCreateSchema, CreateCommentSchema


router = APIRouter(prefix="/article", tags=["Article"])

article_controller = ArticleController()

@router.post("/create", response_model=BaseResponse)
async def add_article(article_data: ArticleCreateSchema,  current_user: dict = Depends(get_current_user)):
    try:
        article_data_dict = article_data.dict()

        article = await article_controller.create_article(article_data_dict, current_user["user_id"])
        
        if article is None:
            raise HTTPException(status_code=500, detail="Failed to create article")
        response_data = {
            "status": 1,
            "message": "Article created successfully",
            "data": {
                "article_id": str(article.id)
            }
        }
        return response_data

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
    
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