"""Основные CRUD операции с комнатами"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Query, status, Depends, HTTPException

from .base import get_room_service
from ..services.room_service import RoomService
from ..schemas.rooms import (
    RoomCreate,
    RoomUpdate,
    RoomResponse,
    RoomWithDetails,
    GenerateLinkResponse,
)

router = APIRouter(prefix="/rooms", tags=["Rooms"])


@router.get("/", response_model=List[RoomResponse])
async def list_rooms(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    candidate_id: Optional[UUID] = None,
    interviewer_id: Optional[UUID] = None,
    vacancy_id: Optional[UUID] = None,
    service: RoomService = Depends(get_room_service),
):
    """Список комнат с фильтрацией"""
    rooms = await service.list_rooms(
        skip=skip,
        limit=limit,
        candidate_id=candidate_id,
        interviewer_id=interviewer_id,
        vacancy_id=vacancy_id,
    )
    return rooms


@router.post("/", response_model=GenerateLinkResponse, status_code=status.HTTP_201_CREATED)
async def create_room(
    room_data: RoomCreate,
    service: RoomService = Depends(get_room_service),
):
    """Создание комнаты"""
    room = await service.create_room(room_data)
    await service.db.commit()
    await service.db.refresh(room)
    return GenerateLinkResponse(room_id=room.id, link=room.link)


@router.get("/{room_id}", response_model=RoomResponse)
async def get_room(
    room_id: UUID,
    service: RoomService = Depends(get_room_service),
):
    """Получение комнаты по ID"""
    room = await service.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room


@router.get("/by-link/{link}", response_model=RoomResponse)
async def get_room_by_link(
    link: str,
    service: RoomService = Depends(get_room_service),
):
    """Получение комнаты по ссылке"""
    room = await service.get_room_by_link(link)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room


@router.put("/{room_id}", response_model=RoomResponse)
async def update_room(
    room_id: UUID,
    room_data: RoomUpdate,
    service: RoomService = Depends(get_room_service),
):
    """Обновление комнаты"""
    room = await service.update_room(room_id, room_data)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    await service.db.commit()
    await service.db.refresh(room)
    return room


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room(
    room_id: UUID,
    service: RoomService = Depends(get_room_service),
):
    """Удаление комнаты"""
    deleted = await service.delete_room(room_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Room not found")
    await service.db.commit()


@router.get("/{room_id}/details", response_model=RoomWithDetails)
async def get_room_with_details(
    room_id: UUID,
    service: RoomService = Depends(get_room_service),
):
    """Получение комнаты со всеми связанными данными"""
    details = await service.get_room_with_details(room_id)
    if not details:
        raise HTTPException(status_code=404, detail="Room not found")
    return details