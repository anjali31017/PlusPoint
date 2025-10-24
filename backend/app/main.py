from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.database.mysql import connect_to_mysql, close_mysql_connection, get_session
from app.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting application...")
    await connect_to_mysql()
    async with db.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    print("Shutting down application...")
    await close_mysql_connection()

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
    response = await call_next(request)
    return response

@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    try:
        session = get_session()
        request.state.db = session
        response = await call_next(request)
        return response
    except ConnectionError:
        print("Database connection lost, attempting to reconnect...")
        await connect_to_mysql()
        session = get_session()
        request.state.db = session
        return await call_next(request)
    finally:
        if hasattr(request.state, "db"):
            await request.state.db.close()
