from fastapi import APIRouter, Query, status
from typing import List
from uuid import UUID
from app.schemas.session import NoteCreate, NoteResponse

router = APIRouter(prefix="/sessions/{session_id}/notes", tags=["Notes"])


@router.get("/", response_model=List[NoteResponse])
async def get_session_notes(
    session_id: UUID,
    limit: int = Query(100, ge=1, le=500),
    skip: int = Query(0, ge=0),
):
    """Получить все заметки сессии"""
    pass


@router.post("/", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(session_id: UUID, note_data: NoteCreate):
    """Создать заметку (только для интервьюера)"""
    pass


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(session_id: UUID, note_id: UUID):
    """Получить заметку по ID"""
    pass


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(session_id: UUID, note_id: UUID):
    """Удалить заметку"""
    pass