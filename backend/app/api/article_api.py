from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks 

from app.controller.user_controller import UserController
from app.models.users import UserModel
from app.schema.user_schema import LogoutSchema, UserCreateSchema, LoginSchema, UserProfileSchema
from app.controller.token_controller import create_token_pair, get_current_user
from app.models.token import RefreshTokenModel
from app.schema.base_schema import BaseResponse
from app.controller.email_controller import send_otp_email
from app.schema.email_schema import OTPVerifySchema
from app.controller.article_controller import ArticleController
from app.schema.article_schema import ArticleCreateSchema


router = APIRouter(prefix="/article", tags=["Article"])

article_controller = ArticleController()

@router.post("/create", response_model=BaseResponse)
async def add_article(article_data: ArticleCreateSchema):
    try:
        article_data_dict = article_data.dict()

        article = await article_controller.create_article(article_data_dict)
        
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