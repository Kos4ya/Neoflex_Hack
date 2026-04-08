from fastapi import APIRouter, Query, status
from typing import List, Optional
from uuid import UUID
from app.schemas.session import (
    SessionCreate, SessionUpdate, SessionResponse, SessionAction
)
from app.core.constants import SessionStatus

router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.get("/", response_model=List[SessionResponse])
async def list_sessions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[SessionStatus] = None,
    interviewer_id: Optional[UUID] = None,
    candidate_id: Optional[UUID] = None,
):
    """Список сессий"""
    pass


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: UUID):
    """Получение сессии по ID"""
    pass


@router.post("/", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(session_data: SessionCreate):
    """Создание новой сессии интервью"""
    pass


@router.put("/{session_id}", response_model=SessionResponse)
async def update_session(session_id: UUID, session_data: SessionUpdate):
    """Обновление сессии"""
    pass


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(session_id: UUID):
    """Удаление сессии (отмена)"""
    pass


@router.post("/{session_id}/action", response_model=SessionResponse)
async def session_action(session_id: UUID, action: SessionAction):
    """
    Действие над сессией:
    - start - начать интервью
    - pause - поставить на паузу
    - resume - возобновить
    - complete - завершить
    - cancel - отменить
    """
    pass


@router.get("/interviewer/{interviewer_id}", response_model=List[SessionResponse])
async def get_interviewer_sessions(
    interviewer_id: UUID,
    status: Optional[SessionStatus] = None,
    limit: int = Query(50, ge=1, le=200),
):
    """Сессии интервьюера"""
    pass


@router.get("/candidate/{candidate_id}", response_model=List[SessionResponse])
async def get_candidate_sessions(
    candidate_id: UUID,
    limit: int = Query(50, ge=1, le=200),
):
    """Сессии кандидата"""
    pass


@router.get("/vacancy/{vacancy_id}", response_model=List[SessionResponse])
async def get_vacancy_sessions(vacancy_id: UUID):
    """Сессии по вакансии"""
    pass