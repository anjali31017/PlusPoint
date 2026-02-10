

from app.models.admin import AdminModel
from app.models.report import ReportModel
from app.models.endorse import EndorsementModel
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.config import settings
from app.models.users import UserModel 
from app.models.firm import FirmModel
from app.models.subscription import SubscriptionModel
from app.models.comment import CommentModel
from app.models.article import ArticleModel, ArticleLikeModel
from app.models.token import RefreshTokenModel
from app.models.notification import NotificationModel
from app.models.kyc import KYCModel

client: AsyncIOMotorClient | None = None

async def connect_to_mongo():
    """
    Establish a MongoDB connection and initialize Beanie models.
    """
    global client
    try:
        if client is None:
            client = AsyncIOMotorClient(settings.MONGODB_URI)
            db = client[settings.MONGO_DB_NAME]
            await init_beanie(database=db, document_models=[
                UserModel, 
                FirmModel, 
                SubscriptionModel, 
                CommentModel, 
                ArticleModel, 
                ArticleLikeModel, 
                RefreshTokenModel,
                NotificationModel,
                KYCModel,
                AdminModel,
                ReportModel,
                EndorsementModel,
                ])
            print("Connected to MongoDB with Beanie")
    except Exception as e:
        print(f"Could not connect to MongoDB: {e}")
        await close_mongo_connection()

async def close_mongo_connection():
    """
    Close the MongoDB connection.
    """
    global client
    if client is not None:
        client.close()
        client = None
        print("MongoDB connection closed")

def get_db():
    """
    Return the Beanie database instance (optional).
    """
    if client is None:
        raise ConnectionError("Database not connected")
    return client[settings.MONGO_DB_NAME]

