from uuid import UUID
from typing import Optional
from fastapi import APIRouter, status, Depends, HTTPException, Query

from .base import get_room_service
from ..services.room_service import RoomService
from ..schemas.rooms import NoteCreate, NoteUpdate, NoteResponse

router = APIRouter(prefix="/rooms", tags=["Notes"])


@router.get("/{room_id}/notes", response_model=list[NoteResponse])
async def get_room_notes(
    room_id: UUID,
    service: RoomService = Depends(get_room_service),
):
    """Получить все заметки комнаты"""
    room = await service.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    notes = await service.get_room_notes(room_id)
    return notes


@router.post("/{room_id}/notes", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    room_id: UUID,
    note_data: NoteCreate,
    time_offset: Optional[int] = Query(None, description="Время от начала интервью в секундах"),
    service: RoomService = Depends(get_room_service),
):
    """Создать заметку в комнате"""
    room = await service.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    note = await service.create_note(room_id, note_data, time_offset)
    if not note:
        raise HTTPException(status_code=404, detail="Room not found")

    await service.db.commit()
    await service.db.refresh(note)
    return note


@router.put("/notes/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: UUID,
    note_data: NoteUpdate,
    service: RoomService = Depends(get_room_service),
):
    """Обновить заметку"""
    note = await service.update_note(note_id, note_data)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    await service.db.commit()
    await service.db.refresh(note)
    return note


@router.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: UUID,
    service: RoomService = Depends(get_room_service),
):
    """Удалить заметку"""
    deleted = await service.delete_note(note_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Note not found")
    await service.db.commit()