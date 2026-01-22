
from typing import List, Optional
from bson import ObjectId
from app.models.article import ArticleModel, ArticleLikeModel, ArticleStatus
from app.models.firm import FirmModel
from app.models.users import UserModel
from datetime import datetime
from fastapi import BackgroundTasks, HTTPException
from pymongo.errors import DuplicateKeyError
from app.models.comment import CommentModel
from app.kafka.producer import send_kafka_event
from app.schema.article_schema import ArticleOutSchema



class ArticleController:

    async def create_article(self, article_data: dict, publisher_id: str) -> ArticleModel | None:
        try:
            firm = await FirmModel.find_one(FirmModel.firm_username == article_data['firm_username'])
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
            # background_tasks.add_task(
            #     send_kafka_event("article.like", {
            #     "publisher_id": str(article.publisher_id.id),
            #     "firm_id": str(article.firm_id.id),
            #     "article_id": str(article.id),
            #     "article_title": article.title,
            #     "user_id": u_id,
            # })
            # )
            
            response = {
                    "status": "liked",
                    "data" : kafka_like_event
                }
            return response
        except Exception as e:
            print(f"Error while liking article: {str(e)}")
            return False


    async def get_article_by_id(self, article_id: str) -> ArticleOutSchema:
        try:
            article = await ArticleModel.find_one(
                ArticleModel.id == ObjectId(article_id),
                ArticleModel.is_deleted == False
            )
            if not article:
                raise HTTPException(status_code=404, detail="Article not found")
            
            publisher = await article.publisher_id.fetch()
            publisher_info = {
                "id": str(publisher.id),
                "username": publisher.username,
                "first_name": publisher.first_name,
                "last_name": publisher.last_name,
            } if publisher else None

            return ArticleOutSchema(
                id=str(article.id),
                title=article.title,
                summary=article.summary,
                like_count=article.like_count,
                tags=article.tags,
                category=article.category,
                published_at=article.published_at,
                publisher=publisher_info
            )
        except Exception as e:
            print(f"Error while liking article: {str(e)}")
            return False
        
    # async def like_article(self, a_id: str, u_id: str):
    #     article_id = ObjectId(a_id)
    #     user_id = ObjectId(u_id)

    #     article = await ArticleModel.get(article_id)
    #     if not article:
    #         raise HTTPException(status_code=404, detail="Article not found")

    #     user = await UserModel.get(user_id)
    #     if not user:
    #         raise HTTPException(status_code=404, detail="User not found")

    #     try:
    #         # TRY LIKE
    #         # print("!!!!!!!!!!!!!!!!!!!! Entering like")
    #         like = ArticleLikeModel(
    #             article_id=article.id,
    #             user_id=user.id
    #         )
    #         await like.insert()
    #         # print(like)
    #         # ATOMIC increment
    #         await ArticleModel.find_one(
    #             ArticleModel.id == article.id,
    #         ).update({"$inc": {"like_count": 1}})
    #         # print("Finddddddddddddddddd")
    #         action = "liked"

    #         # print("ARTICLEEEEE", article)
    #     except DuplicateKeyError:
    #         # ALREADY LIKED → UNLIKE
    #         print("!!!!!!!!!!!!!!!!!!!! Entering duplicate")
    #         await ArticleLikeModel.find_one(
    #             ArticleLikeModel.article_id == article.id,
    #             ArticleLikeModel.user_id == user.id
    #         ).delete()

    #         await ArticleModel.find_one(
    #             ArticleModel.id == article.id
    #         ).update({"$inc": {"like_count": -1}})

            
    #         action = "un-liked"
    #         data = None
            
    #     # Emit Kafka event ONLY for LIKE (optional)
    #     if action == "liked":
    #         firm = await article.firm_id.fetch()
    #         publisher = await article.publisher_id.fetch()
    #         data = {
    #             "publisher_id": str(publisher.id),
    #             "firm_id": str(firm.id),
    #             "article_id": str(article.id),
    #             "article_title": article.title,
    #             "user_id": u_id,
                
    #         }

    #     response = {
    #         "status": action,
    #         "data": data
    #     }
    #     return response




    # @staticmethod
    # async def get_articles_by_firm(
    #     firm_id: ObjectId,
    #     include_publisher: bool = True,
    #     status: Optional[str] = "PUBLISHED",
    # ) -> List[dict]:
    #     try:
    #         query = [
    #             ArticleModel.firm_id.id == firm_id,
    #             ArticleModel.is_deleted == False,
    #         ]
    #         if status:
    #             query.append(ArticleModel.status == status)

    #         articles = await ArticleModel.find(*query).sort(-ArticleModel.published_at).to_list()
    #         result = []

    #         for article in articles:
    #             article_dict = {
    #                 "id": str(article.id),
    #                 "title": article.title,
    #                 "summary": article.summary,
    #                 "content_text": article.content_text,
    #                 "published_at": article.published_at,
    #             }

    #             if include_publisher:
    #                 await article.fetch_link(ArticleModel.publisher_id)
    #                 article_dict["publisher"] = {
    #                     "username": article.publisher_id.username,
    #                     "first_name": article.publisher_id.first_name,
    #                     "last_name": article.publisher_id.last_name,
    #                     "profile_picture_url": article.publisher_id.profile_picture_url,
    #                 }

    #             result.append(article_dict)

    #         return result
    #     except Exception as e:
    #         return str(e)
        
    # @staticmethod
    # async def get_article_by_id(
    #     article_id: str,
    #     include_publisher: bool = True,
    # ) -> Optional[dict]:
    #     try:
    #         if isinstance(article_id, str):
    #             if not ObjectId.is_valid(article_id):
    #                 return None  # Invalid ID
    #             article_id = ObjectId(article_id)

    #         # Use find_one() — returns a single document, not a cursor
    #         article = await ArticleModel.find_one(
    #             ArticleModel.id == article_id,
    #             ArticleModel.is_deleted == False
    #         )

    #         if not article:
    #             return None

    #         # Include publisher info
    #         article_dict = {
    #             "id": str(article.id),
    #             "title": article.title,
    #             "summary": article.summary,
    #             "content_text": article.content_text,
    #             "published_at": article.published_at,
    #         }

    #         if include_publisher:
    #             await article.fetch_link(ArticleModel.publisher_id)
    #             article_dict["publisher"] = {
    #                 "username": article.publisher_id.username,
    #                 "first_name": article.publisher_id.first_name,
    #                 "last_name": article.publisher_id.last_name,
    #                 "profile_picture_url": article.publisher_id.profile_picture_url,
    #             }

    #         return article_dict
    #     except Exception as e:
    #         return str(e)