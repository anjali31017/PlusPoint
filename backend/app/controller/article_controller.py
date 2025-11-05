from bson import ObjectId
from app.models.article import ArticleModel
from app.models.firm import FirmModel
from app.models.users import UserModel
from typing import Dict
from datetime import datetime
from fastapi import HTTPException

class ArticleController:

    async def create_article(self, article_data: dict) -> ArticleModel | None:
        try:
            # Fetch the firm and publisher (user) based on provided IDs
            firm = await FirmModel.get(article_data['firm_id'])
            publisher = await UserModel.get(article_data['publisher_id'])

            # If firm or publisher doesn't exist, raise an exception
            if not firm:
                raise HTTPException(status_code=404, detail="Firm not found")
            if not publisher:
                raise HTTPException(status_code=404, detail="Publisher (User) not found")
            obj_id = ObjectId(article_data['publisher_id'])
            is_publisher_in_firm = any(publisher_info.publisher_user_id.id == obj_id for publisher_info in firm.publishers)

            if not is_publisher_in_firm:
                raise HTTPException(status_code=400, detail="User is not associated with the provided firm")
            
            # Create the article document
            article = ArticleModel(
               **article_data
               )

            # Insert the article into the database
            await article.insert()

            return article

        except Exception as e:
            # Handle any unexpected errors
            print(f"Error while creating article: {str(e)}")
            return None