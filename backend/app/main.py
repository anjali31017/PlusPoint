from fastapi import FastAPI
from app.config import settings
from starlette.middleware.cors import CORSMiddleware

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)