from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from app.sse.sse_manager import sse_connection_manager
import json
import asyncio
from fastapi import status
from app.controller.token_controller import get_current_user

from bson import ObjectId
from fastapi import APIRouter, Depends, File, UploadFile, Form
from app.models.kyc import KYCModel
from fastapi import APIRouter, Depends, HTTPException
from app.controller.token_controller import get_current_user
from app.schema.base_schema import BaseResponse
from fastapi import status
from app.schema.kyc_schema import KYCSchema
from app.controller.kyc_controller import KYCController
import os
from app.models.notification import NotificationModel
from bson import ObjectId
from datetime import datetime
import asyncio
import json
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from app.sse.sse_manager import SSEManager
from app.models.article import ArticleLikeModel, ArticleModel  # your DB model for articles
from app.api.article_api import get_quicktake
from app.models.endorse import EndorsementModel
from app.models.report import ReportModel  # function to fetch daily feed


router = APIRouter(prefix="/sse", tags=["sse"])


from fastapi import Query
headers = {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Access-Control-Allow-Origin": "http://127.0.0.1:3000",
        "Access-Control-Allow-Credentials": "true",
    }


@router.get("/notifications")
async def sse_notifications(
    request: Request,
    token: str = Query(...),  # <- JWT from frontend
):
    auth = "Bearer " + token
    current_user = await get_current_user(auth) 
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token, Login to continue",
        )

    user_id = current_user["user_id"]
    queue = await sse_connection_manager.connect(user_id)
    print(f"User {user_id} connected to SSE")
    
        
    async def event_stream():
        try:
            while True:
                if await request.is_disconnected():
                    print(f"Client {user_id} disconnected")
                    break

                try:
                    message = await asyncio.wait_for(queue.get(), timeout=10)
                    yield f"data: {json.dumps(message)}\n\n"
                except asyncio.TimeoutError:
                    yield 'data: {"type": "heartbeat"}\n\n'

        except asyncio.CancelledError:
            await sse_connection_manager.disconnect(user_id, queue)
            print(f"SSE cancelled for user {user_id}")
            return

        finally:
            await sse_connection_manager.disconnect(user_id, queue)
            print(f"SSE cleaned up for user {user_id}")

    

    return StreamingResponse(event_stream(), media_type="text/event-stream", headers=headers)


@router.get("/list")
async def list_notifications(current_user: dict = Depends(get_current_user)):
    """
    Return the last `limit` notifications for the current user, sorted by newest first.
    """
    try:
        user_id = ObjectId(current_user["user_id"])
        notifications = (
            await NotificationModel.find(NotificationModel.send_to.id == user_id)
            .sort("-created_at")
            .to_list()
        )

        return {"data": notifications}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )








# Keep a queue of last N articles to replay to new connections
LAST_N_ARTICLES = 50
recent_articles: asyncio.Queue = asyncio.Queue(maxsize=LAST_N_ARTICLES)

async def add_to_recent_articles(article: dict):
    if recent_articles.full():
        await recent_articles.get()
    await recent_articles.put(article)



async def hydrate_article_for_user(article: dict, user_id: str):

    # IMPORTANT: make a copy so we don't modify shared object
    hydrated = article.copy()

    article_id = ObjectId(hydrated["article_id"])

    liked = await ArticleLikeModel.find_one(
        ArticleLikeModel.article_id.id == article_id,
        ArticleLikeModel.user_id.id == ObjectId(user_id)
    )

    endorsed = await EndorsementModel.find_one(
        EndorsementModel.article_id.id == article_id,
        EndorsementModel.user_id.id == ObjectId(user_id)
    )

    reported = await ReportModel.find_one(
        ReportModel.article_id.id == article_id,
        ReportModel.user_id.id == ObjectId(user_id),
        ReportModel.is_deleted == False
    )

    hydrated["liked"] = bool(liked)
    hydrated["endorsed"] = bool(endorsed)
    hydrated["reported"] = bool(reported)

    return hydrated



@router.get("/feed")
async def sse_feed(request: Request, token: str = Query(...)):

    auth = "Bearer " + token
    current_user = await get_current_user(auth)

    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token, Login to continue",
        )

    user_id = current_user["user_id"]

    # connect user
    queue = await sse_connection_manager.connect(user_id)

    # replay recent BASE articles → hydrate per user
    recent = list(recent_articles._queue)

    for article in recent:
        hydrated = await hydrate_article_for_user(article, user_id)
        await queue.put(hydrated)

    # if empty → fetch initial feed
    if recent_articles.empty():
        quicktake_feed = await get_quicktake(
            page=1,
            page_size=10,
            user_id=user_id
        )

        for article in quicktake_feed:
            # await add_to_recent_articles(article)

            hydrated = await hydrate_article_for_user(article, user_id)
            await add_to_recent_articles(hydrated)
            await queue.put(hydrated)

    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    break

                try:
                    message = await asyncio.wait_for(queue.get(), timeout=10)
                    yield f"data: {json.dumps(message)}\n\n"

                except asyncio.TimeoutError:
                    yield 'data: {"type": "heartbeat"}\n\n'

        finally:
            await sse_connection_manager.disconnect(user_id, queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers=headers,
    )
    