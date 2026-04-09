from typing import Any
import httpx

from app.core.config import settings


class RoomsClient:
    def __init__(self) -> None:
        self.base_url = settings.ROOMS_SERVICE_URL.rstrip("/")

    async def get_room(self, room_id: str) -> dict[str, Any]:
        url = f"{self.base_url}/rooms/{room_id}"
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()

    async def get_current_code(self, room_id: str) -> dict[str, Any]:
        url = f"{self.base_url}/rooms/{room_id}/code/current"
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()

    async def save_current_code(self, room_id: str, code_body: str, version: int) -> dict[str, Any]:
        url = f"{self.base_url}/rooms/{room_id}/code/current"
        payload = {
            "code_body": code_body,
            "version": version,
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.put(url, json=payload)
            response.raise_for_status()
            return response.json()