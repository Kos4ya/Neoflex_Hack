from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.clients.rooms_client import RoomsClient
from app.schemas.ws_messages import (
    EditorInitMessage,
    EditorSyncedMessage,
    ErrorMessage,
    PresenceMessage,
)
from app.services.connection_manager import ConnectionManager
from app.services.persistence_service import PersistenceService
from app.services.room_state_service import RoomStateService

router = APIRouter()

rooms_client = RoomsClient()
connection_manager = ConnectionManager()
room_state_service = RoomStateService(rooms_client=rooms_client)
persistence_service = PersistenceService(
    room_state_service=room_state_service,
    rooms_client=rooms_client,
)

DEBUG_ALLOW_USER_ID_QUERY = True

def resolve_role(user_id: str, room: dict) -> str | None:
    if str(room["candidate_id"]) == str(user_id):
        return "candidate"
    if str(room["interviewer_id"]) == str(user_id):
        return "interviewer"
    return None


@router.websocket("/ws/rooms/{room_id}")
async def room_editor_ws(websocket: WebSocket, room_id: str):

    username = websocket.query_params.get("username", "anonymous")

    await connection_manager.connect(room_id, websocket)

    try:
        state = await room_state_service.load_or_create_state(room_id)

        # INIT
        await connection_manager.send_json(
            websocket,
            {
                "type": "editor.init",
                "room_id": room_id,
                "code_body": state.code_body,
                "version": state.version,
            }
        )

        # presence
        await connection_manager.broadcast(
            room_id,
            {
                "type": "presence",
                "room_id": room_id,
                "online_count": connection_manager.count_connections(room_id),
            }
        )

        while True:
            message = await websocket.receive_json()
            msg_type = message.get("type")

            # 🔥 ВСЕ МОГУТ РЕДАКТИРОВАТЬ
            if msg_type == "editor.update":

                code_body = message.get("code_body", "")

                state = await room_state_service.apply_update(
                    room_id,
                    code_body
                )

                await connection_manager.broadcast(
                    room_id,
                    {
                        "type": "editor.synced",
                        "room_id": room_id,
                        "code_body": state.code_body,
                        "version": state.version,
                        "updated_by": username,
                    }
                )

                await persistence_service.schedule_save(room_id)

            elif msg_type == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        connection_manager.disconnect(room_id, websocket)

        await connection_manager.broadcast(
            room_id,
            {
                "type": "presence",
                "room_id": room_id,
                "online_count": connection_manager.count_connections(room_id),
            }
        )

        await persistence_service.force_save(room_id)