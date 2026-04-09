from typing import Optional
from uuid import UUID
from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.services.room_service import RoomService


async def get_room_service(db: AsyncSession = Depends(get_db)) -> RoomService:
    """Зависимость для получения сервиса комнат"""
    return RoomService(db)


# Общие параметры запроса для пагинации
class PaginationParams:
    def __init__(
        self,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=500),
    ):
        self.skip = skip
        self.limit = limit


VALID_ROOM_STATUSES = ["created", "active", "completed", "cancelled"]


def validate_room_status(status: str) -> bool:
    """Проверка валидности статуса комнаты"""
    return status in VALID_ROOM_STATUSES