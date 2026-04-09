from app.models.state import RoomState
from app.clients.rooms_client import RoomsClient


class RoomStateService:
    def __init__(self, rooms_client: RoomsClient) -> None:
        self.rooms_client = rooms_client
        self._states: dict[str, RoomState] = {}

    async def load_or_create_state(self, room_id: str) -> RoomState:
        if room_id in self._states:
            return self._states[room_id]

        current_code = await self.rooms_client.get_current_code(room_id)

        state = RoomState(
            room_id=room_id,
            code_body=current_code.get("code_body", ""),
            version=current_code.get("version", 0),
            last_persisted_version=current_code.get("version", 0),
        )
        self._states[room_id] = state
        return state

    async def apply_update(self, room_id: str, code_body: str) -> RoomState:
        state = await self.load_or_create_state(room_id)

        async with state.lock:
            state.code_body = code_body
            state.version += 1

        return state

    async def get_state(self, room_id: str) -> RoomState:
        return await self.load_or_create_state(room_id)