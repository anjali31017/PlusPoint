from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from app.sse.sse_manager import SSEManager
import json
import asyncio
from fastapi import status
from app.controller.token_controller import get_current_user

router = APIRouter(prefix="/sse", tags=["sse"])
sse_connection_manager = SSEManager()

@router.get("/notifications")
async def sse_notifications(request: Request, current_user: dict = Depends(get_current_user)):
    if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token, Login to continue")
    user_id = current_user["user_id"]
    queue = await sse_connection_manager.connect(user_id)
    print(f"User {user_id} connected to SSE")
    
    async def event_stream():
        try:
            yield f"data: {json.dumps({'type': 'connection_established', 'user_id': user_id})}\n\n"
            while True:
                
                try:
                    # Use asyncio.wait_for to wait for either a message or timeout for heartbeat
                    message = await asyncio.wait_for(queue.get(), timeout=25)  # 25s timeout
                    yield f"data: {json.dumps(message)}\n\n"
                except asyncio.TimeoutError:
                    # Timeout → send heartbeat
                    yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"

                # Check if client disconnected
                
                
                if await request.is_disconnected():
                    print("Client disconnected")
                    sse_connection_manager.disconnect(user_id)
                    break
            #--------------------------
            #code to disconnect if browser closes
            #--------------------------
                message = await queue.get()
                yield f"data: {json.dumps(message)}\n\n"
        except asyncio.CancelledError:
            sse_connection_manager.disconnect(user_id)
            raise

    return StreamingResponse(event_stream(), media_type="text/event-stream")

    
    
    
    # async def event_stream():
    #     try:
    #         # Send initial connection message
    #         yield f"data: {json.dumps({'type': 'connection_established', 'user_id': user_id})}\n\n"

    #         while True:
    #             try:
    #                 # Use asyncio.wait_for to wait for either a message or timeout for heartbeat
    #                 message = await asyncio.wait_for(queue.get(), timeout=25)  # 25s timeout
    #                 yield f"data: {json.dumps(message)}\n\n"
    #             except asyncio.TimeoutError:
    #                 # Timeout → send heartbeat
    #                 yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"

    #             # Check if client disconnected
    #             if await request.is_disconnected():
    #                 print(f"User {user_id} disconnected")
    #                 sse_connection_manager.disconnect(user_id)
    #                 break

    #     except asyncio.CancelledError:
    #         sse_connection_manager.disconnect(user_id)
    #         raise