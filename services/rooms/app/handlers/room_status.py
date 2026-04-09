from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Query, Depends, HTTPException

from .base import get_room_service, validate_room_status
from ..services.room_service import RoomService
from ..schemas.rooms import RoomResponse, RoomDurationResponse

router = APIRouter(prefix="/rooms", tags=["Room Status"])


@router.post("/{room_id}/start", response_model=RoomResponse)
async def start_room(
    room_id: UUID,
    service: RoomService = Depends(get_room_service),
):
    """
    Начать интервью в комнате.
    Статус меняется с 'created' на 'active', проставляется время старта.
    """
    room = await service.start_room(room_id)
    if not room:
        raise HTTPException(
            status_code=400,
            detail="Cannot start room. Room not found or already active/completed"
        )
    await service.db.commit()
    await service.db.refresh(room)
    return room


@router.post("/{room_id}/complete", response_model=RoomResponse)
async def complete_room(
    room_id: UUID,
    service: RoomService = Depends(get_room_service),
):
    """
    Завершить интервью в комнате.
    Статус меняется с 'active' на 'completed', проставляется время окончания.
    """
    room = await service.complete_room(room_id)
    if not room:
        raise HTTPException(
            status_code=400,
            detail="Cannot complete room. Room not found or not active"
        )
    await service.db.commit()
    await service.db.refresh(room)
    return room


@router.post("/{room_id}/cancel", response_model=RoomResponse)
async def cancel_room(
    room_id: UUID,
    service: RoomService = Depends(get_room_service),
):
    """
    Отменить интервью в комнате.
    Статус меняется на 'cancelled'.
    """
    room = await service.cancel_room(room_id)
    if not room:
        raise HTTPException(
            status_code=400,
            detail="Cannot cancel room. Room not found or already completed"
        )
    await service.db.commit()
    await service.db.refresh(room)
    return room


@router.get("/status/active", response_model=List[RoomResponse])
async def get_active_rooms(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    interviewer_id: Optional[UUID] = None,
    service: RoomService = Depends(get_room_service),
):
    """
    Получить все активные комнаты (интервью в процессе).
    Можно отфильтровать по интервьюеру.
    """
    rooms = await service.get_active_rooms(
        skip=skip,
        limit=limit,
        interviewer_id=interviewer_id
    )
    return rooms


@router.get("/status/{status}", response_model=List[RoomResponse])
async def get_rooms_by_status(
    status: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    service: RoomService = Depends(get_room_service),
):
    """
    Получить комнаты по статусу.
    Доступные статусы: created, active, completed, cancelled
    """
    if not validate_room_status(status):
        valid_statuses = ["created", "active", "completed", "cancelled"]
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )

    rooms = await service.get_rooms_by_status(
        status=status,
        skip=skip,
        limit=limit
    )
    return rooms


@router.get("/{room_id}/duration", response_model=RoomDurationResponse)
async def get_room_duration(
    room_id: UUID,
    service: RoomService = Depends(get_room_service),
):
    """
    Получить длительность интервью в комнате.
    """
    duration = await service.get_room_duration(room_id)
    if not duration:
        raise HTTPException(status_code=404, detail="Room not found")

    if duration.get("error"):
        raise HTTPException(status_code=400, detail=duration["error"])

    return duration