import asyncio

from app.core.config import settings
from app.services.room_state_service import RoomStateService
from app.clients.rooms_client import RoomsClient


class PersistenceService:
    def __init__(
        self,
        room_state_service: RoomStateService,
        rooms_client: RoomsClient,
    ) -> None:
        self.room_state_service = room_state_service
        self.rooms_client = rooms_client

    async def schedule_save(self, room_id: str) -> None:
        state = await self.room_state_service.get_state(room_id)

        if state.save_task and not state.save_task.done():
            state.save_task.cancel()

        state.save_task = asyncio.create_task(self._debounced_save(room_id))

    async def _debounced_save(self, room_id: str) -> None:
        try:
            await asyncio.sleep(settings.SAVE_DEBOUNCE_SECONDS)
            await self.force_save(room_id)
        except asyncio.CancelledError:
            pass

    async def force_save(self, room_id: str) -> None:
        state = await self.room_state_service.get_state(room_id)

        async with state.lock:
            if state.version == state.last_persisted_version:
                return

            await self.rooms_client.save_current_code(
                room_id=room_id,
                code_body=state.code_body,
                version=state.version,
            )
            state.last_persisted_version = state.version