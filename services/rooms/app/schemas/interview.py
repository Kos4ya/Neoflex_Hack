from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class InterviewStatusEnum(str, Enum):
    """Статусы интервью"""
    SCHEDULED = "scheduled"
    PENDING_FEEDBACK = "pending_feedback"
    COMPLETED = "completed"


class InterviewBase(BaseModel):
    """Базовые поля интервью"""
    interviewer_id: UUID = Field(..., description="ID интервьюера")
    candidate_id: UUID = Field(..., description="ID кандидата")
    scheduled_at: Optional[datetime] = Field(None, description="Запланированное время")


class InterviewCreate(InterviewBase):
    """Создание интервью"""
    room_id: UUID = Field(..., description="ID комнаты")
    vacancy_id: UUID = Field(..., description="ID вакансии")


class InterviewUpdate(BaseModel):
    """Обновление интервью"""
    interviewer_id: Optional[UUID] = None
    candidate_id: Optional[UUID] = None
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    status: Optional[InterviewStatusEnum] = None
    primary_feedback_id: Optional[UUID] = None



class InterviewResponse(InterviewBase):
    """Полная информация об интервью"""
    id: UUID
    room_id: UUID
    vacancy_id: UUID
    status: InterviewStatusEnum
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    primary_feedback_id: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class InterviewListResponse(BaseModel):
    """Список интервью"""
    items: List[InterviewResponse]
    total: int
    skip: int
    limit: int