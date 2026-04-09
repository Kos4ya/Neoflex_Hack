from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.clients.rooms_client import RoomsClient
from app.schemas.ws_messages import (
    EditorInitMessage,
    EditorSyncedMessage,
    ErrorMessage,
    PresenceMessage,
)
from app.services.auth_service import AuthError, AuthService
from app.services.connection_manager import ConnectionManager
from app.services.persistence_service import PersistenceService
from app.services.room_state_service import RoomStateService

router = APIRouter()

rooms_client = RoomsClient()
auth_service = AuthService()
connection_manager = ConnectionManager()
room_state_service = RoomStateService(rooms_client=rooms_client)
persistence_service = PersistenceService(
    room_state_service=room_state_service,
    rooms_client=rooms_client,
)


def resolve_role(user_id: str, room: dict) -> str | None:
    if str(room["candidate_id"]) == str(user_id):
        return "candidate"
    if str(room["interviewer_id"]) == str(user_id):
        return "interviewer"
    return None


@router.websocket("/ws/rooms/{room_id}")
async def room_editor_ws(websocket: WebSocket, room_id: str):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.accept()
        await websocket.send_json(
            ErrorMessage(
                code="UNAUTHORIZED",
                message="Missing token",
            ).model_dump()
        )
        await websocket.close(code=1008)
        return

    try:
        user_id = auth_service.get_user_id(token)
        room = await rooms_client.get_room(room_id)
    except AuthError:
        await websocket.accept()
        await websocket.send_json(
            ErrorMessage(
                code="UNAUTHORIZED",
                message="Invalid token",
            ).model_dump()
        )
        await websocket.close(code=1008)
        return
    except Exception:
        await websocket.accept()
        await websocket.send_json(
            ErrorMessage(
                code="ROOMS_SERVICE_ERROR",
                message="Could not load room",
            ).model_dump()
        )
        await websocket.close(code=1011)
        return

    role = resolve_role(user_id, room)
    if role is None:
        await websocket.accept()
        await websocket.send_json(
            ErrorMessage(
                code="FORBIDDEN",
                message="You are not a member of this room",
            ).model_dump()
        )
        await websocket.close(code=1008)
        return

    await connection_manager.connect(room_id, websocket)

    try:
        state = await room_state_service.load_or_create_state(room_id)

        await connection_manager.send_json(
            websocket,
            EditorInitMessage(
                room_id=room_id,
                role=role,
                read_only=(role != "candidate"),
                code_body=state.code_body,
                version=state.version,
            ).model_dump()
        )

        await connection_manager.broadcast(
            room_id,
            PresenceMessage(
                room_id=room_id,
                online_count=connection_manager.count_connections(room_id),
            ).model_dump()
        )

        while True:
            message = await websocket.receive_json()
            msg_type = message.get("type")

            if msg_type == "editor.update":
                if role != "candidate":
                    await connection_manager.send_json(
                        websocket,
                        ErrorMessage(
                            code="FORBIDDEN",
                            message="Only candidate can edit code",
                        ).model_dump()
                    )
                    continue

                code_body = message.get("code_body", "")
                state = await room_state_service.apply_update(room_id, code_body)

                await connection_manager.broadcast(
                    room_id,
                    EditorSyncedMessage(
                        room_id=room_id,
                        code_body=state.code_body,
                        version=state.version,
                        updated_by="candidate",
                    ).model_dump()
                )

                await persistence_service.schedule_save(room_id)

            elif msg_type == "ping":
                await connection_manager.send_json(websocket, {"type": "pong"})

    except WebSocketDisconnect:
        connection_manager.disconnect(room_id, websocket)
        await connection_manager.broadcast(
            room_id,
            PresenceMessage(
                room_id=room_id,
                online_count=connection_manager.count_connections(room_id),
            ).model_dump()
        )
        if role == "candidate":
            await persistence_service.force_save(room_id)

    except Exception:
        connection_manager.disconnect(room_id, websocket)
        try:
            await persistence_service.force_save(room_id)
        except Exception:
            pass
        await websocket.close(code=1011)