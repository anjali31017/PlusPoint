
import asyncio
from typing import List, Optional
from bson import ObjectId
from app.models.article import ArticleModel, ArticleLikeModel, ArticleStatus
from app.models.firm import FirmModel
from app.models.users import UserModel
from datetime import datetime, timezone
from fastapi import BackgroundTasks, HTTPException
from pymongo.errors import DuplicateKeyError
from app.models.comment import CommentModel
from app.kafka.producer import send_kafka_event
from app.schema.article_schema import ArticleOutSchema
from app.models.endorse import EndorsementModel
import os


class ArticleController:

    async def create_article(self, firm_id:str, article_data: dict, publisher_id: str) -> ArticleModel | None:
        try:
            firm = await FirmModel.find_one(FirmModel.id == ObjectId(firm_id), FirmModel.is_deleted == False)
            if not firm:
                raise HTTPException(status_code=404, detail="Firm not found")
            obj_id = ObjectId(publisher_id)
            
            baseline = 100
            trust_score = (0.4 * firm.trust_factor + 0.6 * baseline) / 2
            
            
        
            
            article = ArticleModel(
                firm_id=firm,
                publisher_id=publisher_id,
                title=article_data["title"],
                content=article_data["content"],
                status=ArticleStatus.PENDING_REVIEW if trust_score < 40 else article_data["status"],
                category=article_data["category"],
                tags=article_data["tags"],
                hot_topic=article_data["hot_topic"],
                trust_score_snapshot = trust_score,
                moderation_required=True if trust_score < 40 else False,
                published_at=datetime.now() 
            )

            await article.insert()
            return article

        except Exception as e:
            print(f"Error while creating article: {str(e)}")
            return None
        
    async def update_article( self, article_id: str, update_data: dict) -> ArticleModel | None:
        try:
            article = await ArticleModel.find_one(ArticleModel.id == ObjectId(article_id), ArticleModel.is_deleted == False)
            if not article:
                raise HTTPException(status_code=404, detail="Article not found")
            
            for key, value in update_data.items():
                setattr(article, key, value)
            
            result = await article.save()
            if not result:
                print("Failed to update article")
                return None 
            print("Article updated successfully")

            return article           
        except Exception as e:
            print(f"Error while updating article: {str(e)}")
            return None
                         
    async def create_comment(
        self, 
        comment_data :dict, 
        article_id:str, 
        parent_comment_id: str | None,
        user_id: str
        ) -> ArticleModel | None:
        try:
            article = await ArticleModel.find_one(ArticleModel.id == ObjectId(article_id), ArticleModel.is_deleted == False)
            if not article:
                raise HTTPException(status_code=404, detail="Article not found")
            user = await UserModel.find_one(UserModel.id == ObjectId(user_id), UserModel.is_deleted == False)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            if parent_comment_id:
                parent_comment = await CommentModel.find_one(CommentModel.id == ObjectId(parent_comment_id), CommentModel.is_deleted == False)
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


    async def like_article( self, a_id: str, u_id:str) -> ArticleLikeModel:
        try:
            article = await ArticleModel.find_one(ArticleModel.id == ObjectId(a_id), ArticleModel.is_deleted == False)
            if not article:
                raise HTTPException(status_code=404, detail="Article not found")

            user = await UserModel.find_one(UserModel.id == ObjectId(u_id), UserModel.is_deleted == False)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            liked = await ArticleLikeModel.find_one(
                ArticleLikeModel.user_id.id == user.id,
                ArticleLikeModel.article_id.id == article.id
                )
            # print(liked)
            if liked:
                await liked.delete()
                await article.update({"$inc": {"like_count": -1}})
                response = {
                    "status": "un-liked",
                    "data" : None
                }
                return response

            like = ArticleLikeModel( article_id=a_id, user_id=u_id)
            await like.insert()
            await article.update({"$inc": {"like_count": 1}})
            
            firm = await article.firm_id.fetch()
            publisher = await article.publisher_id.fetch()
            kafka_like_event = {
                "publisher_id": str(publisher.id),
                "firm_id": str(firm.id),
                "article_id": str(article.id),
                "article_title": article.title,
                "user_id": u_id,
                
            }

            response = {
                    "status": "liked",
                    "data" : kafka_like_event
                }
            return response
        except Exception as e:
            print(f"Error while liking article: {str(e)}")
            return False


    async def get_article_by_id(self, article_id: str, current_user:dict|None = None ) -> ArticleOutSchema:
        try:
            article = await ArticleModel.find_one(
                ArticleModel.id == ObjectId(article_id),
                ArticleModel.status == ArticleStatus.PUBLISHED,
                ArticleModel.is_deleted == False
            )
            if not article:
                return None
            
            publisher = await article.publisher_id.fetch()
            publisher_info = {
                "id": str(publisher.id),
                "username": publisher.username,
                "first_name": publisher.first_name,
                "last_name": publisher.last_name,
            } if publisher else None

            endorse = False
            like = False
            is_self = False    
            
            if current_user:
                endorsement = await EndorsementModel.find_one(
                    EndorsementModel.user_id.id == ObjectId(current_user["user_id"]),
                    EndorsementModel.article_id.id == article.id
                    )
                endorse = True if endorsement else False
                
                like_result = await ArticleLikeModel.find_one(
                    ArticleLikeModel.user_id.id == ObjectId(current_user["user_id"]),
                    ArticleLikeModel.article_id.id == article.id
                    )
                like = True if like_result else False

                is_self = str(current_user["user_id"]) == str(publisher.id)
                
            return ArticleOutSchema(
                id=str(article.id),
                title=article.title,
                summary=article.summary,
                content=article.content,
                content_text=article.content_text,
                endorse_count=article.endorse_count,
                like_count=article.like_count,
                trust_score_snapshot=article.trust_score_snapshot,
                tags=article.tags,
                category=article.category,
                published_at=article.published_at,
                publisher=publisher_info,
                endorsed=endorse,
                liked=like,
                is_self=is_self,
            )
    
        except Exception as e:
            print(f"Error while liking article: {str(e)}")
            return None
        

    async def get_articles(self, article_id: str, current_user:dict|None = None ) -> ArticleOutSchema:
        try:
            article = await ArticleModel.find_one(
                ArticleModel.id == ObjectId(article_id),
                ArticleModel.is_deleted == False
            )
            if not article:
                return None
            
            publisher = await article.publisher_id.fetch()
            publisher_info = {
                "id": str(publisher.id),
                "username": publisher.username,
                "first_name": publisher.first_name,
                "last_name": publisher.last_name,
            } if publisher else None

            endorse = False
            like = False
            is_self = False    
            
            if current_user:
                endorsement = await EndorsementModel.find_one(
                    EndorsementModel.user_id.id == ObjectId(current_user["user_id"]),
                    EndorsementModel.article_id.id == article.id
                    )
                endorse = True if endorsement else False
                
                like_result = await ArticleLikeModel.find_one(
                    ArticleLikeModel.user_id.id == ObjectId(current_user["user_id"]),
                    ArticleLikeModel.article_id.id == article.id
                    )
                like = True if like_result else False

                is_self = str(current_user["user_id"]) == str(publisher.id)
                
            return ArticleOutSchema(
                id=str(article.id),
                title=article.title,
                summary=article.summary,
                content=article.content,
                content_text=article.content_text,
                endorse_count=article.endorse_count,
                like_count=article.like_count,
                trust_score_snapshot=article.trust_score_snapshot,
                tags=article.tags,
                category=article.category,
                published_at=article.published_at,
                publisher=publisher_info,
                endorsed=endorse,
                liked=like,
                is_self=is_self,
            )
    
        except Exception as e:
            print(f"Error while liking article: {str(e)}")
            return None
        