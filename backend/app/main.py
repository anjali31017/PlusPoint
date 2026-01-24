from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from app.config import settings
import asyncio
import os

# from router.oauth import router as oauth_router
from app.api.user_api import router as user_router
from app.api.admin_api import router as admin_router
from app.api.kyc_api import router as kyc_router
from app.websocket.websocket_endpoints import router as websocket_router
from app.database.connection import connect_to_mongo, close_mongo_connection, get_db
from app.api.refresh_api import router as token_router
from app.api.firm_api import router as firm_router
from app.api.article_api import router as article_router
from app.sse.sse_endpoint import router as sse_router
from app.kafka.producer import start_producer, stop_producer
from app.kafka.consumer.article_consumer import KafkaArticleService
from starlette.middleware.sessions import SessionMiddleware

from app.kafka.consumer.moderation_consumer import ModerationKafkaConsumer
from app.kafka.consumer.like_consumer import KafkaLikeService
from app.kafka.consumer.follow_consumer import KafkaFollowService
from app.utils.trust_factor import background_tf_updater

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting application...")
    await connect_to_mongo()
    await start_producer()
    
    article_consumer = asyncio.create_task(KafkaArticleService.consume_articles())
    like_consumer = asyncio.create_task(KafkaLikeService.consume_likes())
    follow_consumer = asyncio.create_task(KafkaFollowService.consume_follow())
    
    # moderation_consumer = asyncio.create_task(ModerationKafkaConsumer.start())

    asyncio.create_task(background_tf_updater())
    
    try:
        yield

    finally:
        
        print("Shutting down application...")
        KafkaArticleService.is_running = False
        await KafkaArticleService.shutdown()

        KafkaLikeService.is_running = False
        await KafkaLikeService.shutdown()

        KafkaFollowService.is_running = False
        await KafkaFollowService.shutdown()
        
        article_consumer.cancel()
        like_consumer.cancel()
        follow_consumer.cancel()
        
        await asyncio.gather(article_consumer, like_consumer, follow_consumer, return_exceptions=True)
        
    # ModerationKafkaConsumer.is_running = False
    # await ModerationKafkaConsumer.shutdown()

    # try:
    #     await consumer_task.cancel()
    # except:
    #     print("Kafka consumer task cancellation failed or was already cancelled.")
    # await asyncio.gather(consumer_task, return_exceptions=True)
    
        await stop_producer()
        await close_mongo_connection()

        print("Application shutdown complete.")
        
        
app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG, lifespan=lifespan)

origins = [
    "http://127.0.0.1:3000",  # your frontend URL, include port
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_middleware(SessionMiddleware, secret_key=settings.SESSION_SECRET)

# os.makedirs(settings.KYC_UPLOAD_FOLDER, exist_ok=True)

os.makedirs(settings.KYC_UPLOAD_FOLDER, exist_ok=True)
os.makedirs(settings.PROFILE_UPLOAD_FOLDER, exist_ok=True)
os.makedirs(settings.TINYMCE_UPLOAD_FOLDER, exist_ok=True)


# app.mount("/images/profile", StaticFiles(directory="/app/images/profile"), name="profile_images")
# app.mount("/images/kyc", StaticFiles(directory="/app/images/kyc"), name="kyc_images")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"API Call: {request.method} {request.url.path}")
    return await call_next(request)


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    try:
        db = get_db()
        request.state.db = db
        response = await call_next(request)
        return response
    except ConnectionError:
        print("Database connection lost, reconnecting...")
        await connect_to_mongo()
        try:
            db = get_db()
            request.state.db = db
            return await call_next(request)
        except ConnectionError:
            return JSONResponse(
                status_code=503, content={"detail": "Database connection error"}
            )


app.include_router(
    user_router,
    prefix=f"{settings.API_PREFIX}",
    tags=["users"],
)

app.include_router(
    token_router,
    prefix=f"{settings.API_PREFIX}",
    tags=["token"],
)

app.include_router(
    admin_router,
    prefix=f"{settings.API_PREFIX}",
    tags=["admin"],
)

app.include_router(
    firm_router,
    prefix=f"{settings.API_PREFIX}",
    tags=["firm"],
)


app.include_router(
    article_router,
    prefix=f"{settings.API_PREFIX}",
    tags=["article"],
)


app.include_router(
    kyc_router,
    prefix=f"{settings.API_PREFIX}",
    tags=["kyc"],
)


app.include_router(
    websocket_router,
    prefix=f"{settings.WS_PREFIX}",
    tags=["websocket"],
)


app.include_router(sse_router)

# app.include_router(
#     email_otp_router,
#     prefix=f"{settings.API_PREFIX}",
#     tags=["email-otp"],

# )

# @app.middleware("http")
# async def db_session_middleware(request: Request, call_next):
#     try:
#         session = get_session()
#         request.state.db = session
#         response = await call_next(request)
#         return response
#     except ConnectionError:
#         print("Database connection lost, attempting to reconnect...")
#         await connect_to_mysql()
#         session = get_session()
#         request.state.db = session
#         return await call_next(request)
#     finally:
#         if hasattr(request.state, "db"):
#             await request.state.db.close()


# app.include_router(
#     oauth_router,
#     prefix=f"{settings.API_PREFIX}",
#     tags=["oauth"],

# )
