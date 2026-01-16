from typing import List, Optional
from bson import ObjectId
from app.models.article import ArticleModel, ArticleLikeModel
from app.models.firm import FirmModel
from app.models.users import UserModel
from datetime import datetime
from fastapi import HTTPException

from app.models.comment import CommentModel
from app.schema.article_schema import ArticleSearchSchema
from app.models.publisher import PublisherModel


class ArticleController:

    async def create_article(self, article_data: dict, publisher_id: str) -> ArticleModel | None:
        try:
            firm = await FirmModel.find_one(FirmModel.firm_username == article_data['firm_username'])
            if not firm:
                raise HTTPException(status_code=404, detail="Firm not found")
            obj_id = ObjectId(publisher_id)
            is_publisher_in_firm = PublisherModel.find_one(
                PublisherModel.publisher_id.id == obj_id,
                PublisherModel.firm_id.id == firm.id,
                PublisherModel.is_deleted == False,
            )

            if not is_publisher_in_firm:
                raise HTTPException(status_code=400, detail="User is not associated with the provided firm")
            
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

            await article.insert()
            return article

        except Exception as e:
            print(f"Error while creating article: {str(e)}")
            return None
        
    async def update_article( self, article_id: str, update_data: dict) -> ArticleModel | None:
        try:
            article = await ArticleModel.get(ObjectId(article_id))
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

    async def search_articles(
        self,
        publisher_name: Optional[str] = None,
        firm_name: Optional[str] = None,
        keywords: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        content_words: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        hot_topic: Optional[bool] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        sort_by: str = "newest",
        page: int = 1,
        page_size: int = 10
    ):
        try:
            query_filters = {}

            # Publisher filter
            if publisher_name:
                publishers = await UserModel.find(
                    {"$or": [
                        {"username": {"$regex": publisher_name, "$options": "i"}},
                        {"first_name": {"$regex": publisher_name, "$options": "i"}},
                        {"last_name": {"$regex": publisher_name, "$options": "i"}}
                    ]}
                ).to_list()
                publisher_ids = [p.id for p in publishers]
                if publisher_ids:
                    query_filters["publisher_id"] = {"$in": publisher_ids}
                else:
                    return {"total": 0, "articles": []}

            # Firm filter
            if firm_name:
                firms = await FirmModel.find(
                    {"firm_name": {"$regex": firm_name, "$options": "i"}}
                ).to_list()
                firm_ids = [f.id for f in firms]
                if firm_ids:
                    query_filters["firm_id"] = {"$in": firm_ids}
                else:
                    return {"total": 0, "articles": []}

            # Tags, Keywords, Categories
            if tags:
                query_filters["tags"] = {"$in": tags}
            if keywords:
                query_filters["keywords"] = {"$in": keywords}
            if categories:
                query_filters["category"] = {"$in": categories}

            # Hot topic
            if hot_topic is not None:
                query_filters["hot_topic"] = hot_topic

            # Date filtering
            if start_date or end_date:
                query_filters["published_at"] = {}
                if start_date:
                    query_filters["published_at"]["$gte"] = start_date
                if end_date:
                    query_filters["published_at"]["$lte"] = end_date

            # Content words
            if content_words:
                query_filters["$text"] = {"$search": " ".join(content_words)}

            # Sorting
            sort_criteria = [("published_at", -1)]  # default newest
            if sort_by == "oldest":
                sort_criteria = [("published_at", 1)]
            elif sort_by == "most_liked":
                sort_criteria = [("like_count", -1)]

            # Pagination
            skip = (page - 1) * page_size
            limit = page_size

            # Fetch articles
            cursor = ArticleModel.find(query_filters).sort(sort_criteria)
            total = await cursor.count()
            articles = await cursor.skip(skip).limit(limit).to_list()

            return {"total": total, "articles": articles}
        except Exception as e:
            print(f"Error while searching articles: {str(e)}")
            return {"total": 0, "articles": []}
    # async def search_articles(self, search_data: ArticleSearchSchema):
    #     try:
    #         query = {}

    #         if search_data.publisher_id:
    #             query["publisher_id.id"] = ObjectId(search_data.publisher_id)
    #         if search_data.firm_id:
    #             query["firm_id.id"] = ObjectId(search_data.firm_id)
    #         if search_data.hot_topic is not None:
    #             query["hot_topic"] = search_data.hot_topic
    #         if search_data.categories:
    #             query["category"] = {"$in": search_data.categories}
    #         if search_data.tags:
    #             query["tags"] = {"$in": search_data.tags}

    #         # Keyword search in title, content, summary
    #         if search_data.keyword:
    #             regex = {"$regex": search_data.keyword, "$options": "i"}
    #             query["$or"] = [
    #                 {"title": regex},
    #                 {"content": regex},
    #                 {"summary": regex},
    #             ]

    #         # Exclude deleted articles
    #         query["is_deleted"] = False

    #         articles = await ArticleModel.find(query).sort("-published_at").skip(search_data.skip).limit(search_data.limit).to_list()
            
    #         return articles if articles else None
    #     except Exception as e:
    #         print(f"Error while searching articles: {str(e)}")
    #         return str(e)
