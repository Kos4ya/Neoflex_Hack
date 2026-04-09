from collections import defaultdict
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: dict[str, list[WebSocket]] = defaultdict(list)

    async def connect(self, room_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections[room_id].append(websocket)

    def disconnect(self, room_id: str, websocket: WebSocket) -> None:
        if room_id not in self._connections:
            return

        self._connections[room_id] = [
            ws for ws in self._connections[room_id] if ws != websocket
        ]

        if not self._connections[room_id]:
            del self._connections[room_id]

    async def send_json(self, websocket: WebSocket, payload: dict) -> None:
        await websocket.send_json(payload)

    async def broadcast(self, room_id: str, payload: dict) -> None:
        dead_connections: list[WebSocket] = []

        for websocket in self._connections.get(room_id, []):
            try:
                await websocket.send_json(payload)
            except Exception:
                dead_connections.append(websocket)

        for websocket in dead_connections:
            self.disconnect(room_id, websocket)

    def count_connections(self, room_id: str) -> int:
        return len(self._connections.get(room_id, []))