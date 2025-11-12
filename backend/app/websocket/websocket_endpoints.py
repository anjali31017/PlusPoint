# main.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from app.websocket.websocket_manager import ConnectionManager

router = FastAPI()

article_notification_manager = ConnectionManager()

@router.websocket("/notification/{user_id}")
async def websocket_articile_notification_endpoint(websocket: WebSocket, user_id: str):
    connection_id = await article_notification_manager.connect(websocket, user_id)
    try:
        # Optionally notify the client of their UUID
        await websocket.send_json({"type": "connection_established", "connection_id": connection_id})

        while True:
            data = await websocket.receive_text()
            print(f"Received from {user_id}/{connection_id}: {data}")
    except WebSocketDisconnect:
        article_notification_manager.disconnect(user_id, connection_id)
