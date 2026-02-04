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
    # Validate JWT using your existing function
    auth = "Bearer " + token
    current_user = await get_current_user(auth) 
    # current_user = await get_current_user("Bearer") 
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
                    break

                try:
                    message = await asyncio.wait_for(queue.get(), timeout=10)
                    yield f"data: {json.dumps(message)}\n\n"
                except asyncio.TimeoutError:
                    yield 'data: {"type": "heartbeat"}\n\n'
        finally:
            await sse_connection_manager.disconnect(user_id, queue)
        
    # async def event_stream():
    #     try:
    #         while True:
    #             if await request.is_disconnected():
    #                 print(f"Client {user_id} disconnected")
    #                 break

    #             try:
    #                 message = await asyncio.wait_for(queue.get(), timeout=10)
    #                 yield f"data: {json.dumps(message)}\n\n"
    #             except asyncio.TimeoutError:
    #                 yield 'data: {"type": "heartbeat"}\n\n'

    #     except asyncio.CancelledError:
    #         await sse_connection_manager.disconnect(user_id)
    #         print(f"SSE cancelled for user {user_id}")
    #         return

    #     finally:
    #         await sse_connection_manager.disconnect(user_id)
    #         print(f"SSE cleaned up for user {user_id}")

    

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


# @router.get("/unread_count")
# async def get_unread_count(current_user: dict = Depends(get_current_user)):
#     count = await NotificationModel.find(
#         {"send_to": ObjectId(current_user["user_id"]), "read_at": None}
#     ).count()
#     return {"count": count}


# @router.post("/mark_read")
# async def mark_notifications_read(
#     notification_ids: list[str], current_user: dict = Depends(get_current_user)
# ):

#     try:
#         obj_ids = [ObjectId(nid) for nid in notification_ids]
#         data = await NotificationModel.find(NotificationModel.id == obj_ids)
#         data.read_at
#         await NotificationModel.find(
#             {"_id": {"$in": obj_ids}, "send_to": ObjectId(current_user["user_id"])}
#         ).update({"$set": {"read_at": datetime.utcnow()}})
#         return {"status": 1, "message": "Marked as read"}
#     except Exception as e:
#         return {"status": 0, "message": str(e)}


# @router.get("/notifications")
# async def sse_notifications(request: Request, current_user: dict = Depends(get_current_user)):
#     if current_user is None:
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token, Login to continue")
#     user_id = current_user["user_id"]
#     queue = await sse_connection_manager.connect(user_id)
#     print(f"User {user_id} connected to SSE")

#     async def event_stream():
#         try:
#             yield f"data: {json.dumps({'type': 'connection_established', 'user_id': user_id})}\n\n"
#             while True:

#                 try:
#                     # Use asyncio.wait_for to wait for either a message or timeout for heartbeat
#                     message = await asyncio.wait_for(queue.get(), timeout=25)  # 25s timeout
#                     yield f"data: {json.dumps(message)}\n\n"
#                 except asyncio.TimeoutError:
#                     # Timeout → send heartbeat
#                     yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"

#                 # Check if client disconnected


#                 if await request.is_disconnected():
#                     print("Client disconnected")
#                     sse_connection_manager.disconnect(user_id)
#                     break
#             #--------------------------
#             #code to disconnect if browser closes
#             #--------------------------
#                 message = await queue.get()
#                 yield f"data: {json.dumps(message)}\n\n"
#         except asyncio.CancelledError:
#             sse_connection_manager.disconnect(user_id)
#             raise

#     return StreamingResponse(event_stream(), media_type="text/event-stream")
