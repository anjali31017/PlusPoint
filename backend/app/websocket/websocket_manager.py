# connection_manager.py
import uuid
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        # {user_id: {connection_id: websocket}}
        self.active_connections: dict[str, dict[str, WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str | None = None) -> str:
        """Accept and store a new websocket connection."""
        await websocket.accept()
        connection_id = str(uuid.uuid4())

        # handle anonymous or user-scoped connections
        user_key = user_id or "anonymous"
        if user_key not in self.active_connections:
            self.active_connections[user_key] = {}
        self.active_connections[user_key][connection_id] = websocket

        return connection_id

    def disconnect(self, user_id: str | None, connection_id: str):
        """Remove websocket connection by ID."""
        user_key = user_id or "anonymous"
        if user_key in self.active_connections:
            self.active_connections[user_key].pop(connection_id, None)
            if not self.active_connections[user_key]:
                del self.active_connections[user_key]

    # async def send_personal_message(self, message: str, user_id: str):
    #     """Send a message to all connections of a user."""
    #     user_key = user_id or "anonymous"
    #     for ws in self.active_connections.get(user_key, {}).values():
    #         await ws.send_text(message)
            
    # async def send_personal_message(self, message: dict | str, user_id: str):
    #     user_key = user_id or "anonymous"
    #     if user_key not in self.active_connections:
    #         print(f"User {user_key} not connected, skipping message")
    #     for ws in self.active_connections.get(user_key, {}).values():
    #         if isinstance(message, dict):
    #             await ws.send_json(message)
    #         else:
    #             await ws.send_text(message)

    async def send_personal_message(self, message: dict | str, user_id: str):
        user_key = user_id or "anonymous"
        if user_key not in self.active_connections:
            print(f"User {user_key} not connected, skipping message")
            return

        for ws in self.active_connections[user_key].values():
            try:
                if isinstance(message, dict):
                    await ws.send_json(message)
                else:
                    await ws.send_text(message)
            except Exception as e:
                print(f"Failed to send message to {user_key}: {e}")


    async def send_to_connection(self, message: str, user_id: str, connection_id: str):
        """Send a message to a specific connection."""
        ws = self.active_connections.get(user_id, {}).get(connection_id)
        if ws:
            await ws.send_text(message)

    async def broadcast(self, message: str):
        """Send to all connections (all users)."""
        for user_conns in self.active_connections.values():
            for ws in user_conns.values():
                await ws.send_text(message)
