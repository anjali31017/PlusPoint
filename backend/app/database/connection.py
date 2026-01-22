

from app.models.admin import AdminModel
from app.models.report import ReportModel
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



# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
# from sqlalchemy.orm import sessionmaker, declarative_base
# from config import settings
# from builtins import print

# Base = declarative_base()

# class Database:
#     engine = None
#     SessionLocal = None

#     @classmethod
#     async def connect_to_mysql(cls):
#         try:
#             if cls.engine is None:
#                 cls.engine = create_async_engine(
#                     settings.MYSQL_URI,
#                     echo=settings.DEBUG,
#                     pool_pre_ping=True
#                 )
#                 cls.SessionLocal = sessionmaker(
#                     bind=cls.engine,
#                     class_=AsyncSession,
#                     expire_on_commit=False
#                 )
#                 print("Successfully connected to MySQL")
#         except Exception as e:
#             print(f"Could not connect to MySQL: {e}")
#             await cls.close_mysql_connection()

#     @classmethod
#     async def close_mysql_connection(cls):
#         if cls.engine is not None:
#             await cls.engine.dispose()
#             cls.engine = None
#             cls.SessionLocal = None
#             print("MySQL connection closed")

#     @classmethod
#     def get_session(cls) -> AsyncSession:
#         if cls.SessionLocal is None:
#             raise ConnectionError("Database not connected")
#         return cls.SessionLocal()

# # Create a global instance
# db = Database()

# # Export helper functions
# async def connect_to_mysql():
#     await db.connect_to_mysql()

# async def close_mysql_connection():
#     await db.close_mysql_connection()

# def get_session():
#     return db.get_session()
