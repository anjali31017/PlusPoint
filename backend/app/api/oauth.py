from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from utils.oauth_client import get_google_oauth_url, get_github_oauth_url
from controllers.auth_controller import handle_google_callback, handle_github_callback
from database.connection import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.get("/google/login")
async def google_login():
    return {"auth_url": get_google_oauth_url()}

@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    code = request.query_params.get("code")
    return await handle_google_callback(code, db)

@router.get("/github/login")
async def github_login():
    return {"auth_url": get_github_oauth_url()}

@router.get("/github/callback")
async def github_callback(request: Request, db: Session = Depends(get_db)):
    code = request.query_params.get("code")
    return await handle_github_callback(code, db)
