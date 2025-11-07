from bson import ObjectId
from app.models.article import ArticleModel, ArticleLikeModel
from app.models.firm import FirmModel
from app.models.users import UserModel
from typing import Dict
from datetime import datetime
from fastapi import HTTPException

from app.models.comment import CommentModel


class ArticleController:

    async def create_article(self, article_data: dict, publisher_id: str) -> ArticleModel | None:
        try:
            firm = await FirmModel.find_one(FirmModel.firm_username == article_data['firm_username'])
            if not firm:
                raise HTTPException(status_code=404, detail="Firm not found")
            obj_id = ObjectId(publisher_id)
            is_publisher_in_firm = any(
                publisher_info.publisher_user_id.id == obj_id 
                for publisher_info in firm.publishers or []
                )

            if not is_publisher_in_firm:
                raise HTTPException(status_code=400, detail="User is not associated with the provided firm")
            
            # Create the article document
            article = ArticleModel(
                firm_id=firm,
                publisher_id=publisher_id,
                title=article_data["title"],
                content=article_data["content"],
                category=article_data["category"],
                tags=article_data["tags"],
                hot_topic=article_data["hot_topic"],
                published_at=datetime.now()
            )

            # Insert the article into the database
            await article.insert()

            return article

        except Exception as e:
            # Handle any unexpected errors
            print(f"Error while creating article: {str(e)}")
            return None
        
    
    async def create_comment(
        self, 
        comment_data :dict, 
        article_id:str, 
        parent_comment_id: str | None,
        user_id: str
        ) -> ArticleModel | None:
        try:
            article = await ArticleModel.get(ObjectId(article_id))
            if not article:
                raise HTTPException(status_code=404, detail="Article not found")
            user = await UserModel.get(ObjectId(user_id))
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            if parent_comment_id:
                parent_comment = await CommentModel.get(ObjectId(parent_comment_id))
                if not parent_comment:
                    raise HTTPException(status_code=404, detail="Parent comment not found")

            comment = CommentModel(
                article_id= article_id,
                user_id= user_id,
                content= comment_data["content"],
                parent_comment_id= ObjectId(parent_comment_id) if parent_comment_id else None,
                posted_at= datetime.now()
            )

            await comment.insert()

            return comment

        except Exception as e:
            print(f"Error while adding comment: {str(e)}")
            return None 
        
    # async def like_article(self, article_id: str, user_id: str):
    #     try:
    #         user = await UserModel.get(ObjectId(user_id))
    #         if not user:
    #             raise HTTPException(status_code=404, detail="User not found")

    #         # Validate article exists
    #         article = await ArticleModel.get(ObjectId(article_id))
    #         if not article:
    #             raise HTTPException(status_code=404, detail="Article not found")
            
    #         # Check if like already exists
    #         existing_like = await LikeModel.find_one(
    #             LikeModel.user_id.id == user_id,
    #             LikeModel.article_id.id == article_id
    #         )
    #         if existing_like:
    #             # Optional: return existing like instead of creating new
    #             return existing_like

    #         # Create new like
    #         like = LikeModel(user_id=user, article_id=article, created_at=datetime.now())
    #         await like.insert()
    #         return like
    #     except Exception as e:
    #         print("Exception: ", str(e))
    #         return e
    
    async def like_article(
        self, 
        a_id: str,
        u_id:str
        ) -> ArticleLikeModel:
        try:
            article = await ArticleModel.get(ObjectId(a_id))
            if not article:
                raise HTTPException(status_code=404, detail="Article not found")

            user = await UserModel.get(ObjectId(u_id))
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            liked = await ArticleLikeModel.find_one(
                ArticleLikeModel.user_id.id == user.id,
                ArticleLikeModel.article_id.id == article.id
                )

            if liked:
                await liked.delete()
                return "un-liked"

            like = ArticleLikeModel(
                article_id=a_id,
                user_id=u_id
                )
            
            await like.insert()
            return "liked"
        except Exception as e:
            print(f"Error while liking article: {str(e)}")
            return False
