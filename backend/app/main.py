from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
# from router.oauth import router as oauth_router
from app.api.user_api import router as user_router
from app.database.connection import connect_to_mongo, close_mongo_connection, get_db
from app.api.refresh_api import router as token_router
from app.api.firm_api import router as firm_router
from app.api.article_api import router as article_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting application...")
    await connect_to_mongo()
    yield
    print("Shutting down application...")
    await close_mongo_connection()

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
                status_code=503,
                content={"detail": "Database connection error"}
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
    firm_router, 
    prefix=f"{settings.API_PREFIX}", 
    tags=["firm"],

)


app.include_router(
    article_router, 
    prefix=f"{settings.API_PREFIX}", 
    tags=["article"],

)


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