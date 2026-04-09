from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional, List
from enum import Enum


class CandidateStatus(str, Enum):
    """Статус кандидата по вакансии"""
    PENDING = "pending"  # на рассмотрении
    REVIEWED = "reviewed"  # просмотрено


class VacancyBase(BaseModel):
    """Базовые поля вакансии"""
    name: str = Field(..., min_length=1, max_length=255, description="Название вакансии")


class VacancyCreate(VacancyBase):
    """Схема для создания вакансии"""
    pass


class VacancyUpdate(BaseModel):
    """Схема для обновления вакансии"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)


class VacancyResponse(VacancyBase):
    """Схема для ответа API"""
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CandidateBase(BaseModel):
    """Базовые поля кандидата"""
    name: str = Field(..., min_length=1, max_length=100, description="Имя кандидата")
    surname: str = Field(..., min_length=1, max_length=100, description="Фамилия кандидата")


class CandidateCreate(CandidateBase):
    """Схема для создания кандидата"""
    pass


class CandidateUpdate(BaseModel):
    """Схема для обновления кандидата"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    surname: Optional[str] = Field(None, min_length=1, max_length=100)


class CandidateResponse(CandidateBase):
    """Схема для ответа API"""
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class VacancyCandidateBase(BaseModel):
    """Базовые поля связи вакансия-кандидат"""
    vacancy_id: UUID = Field(..., description="ID вакансии")
    candidate_id: UUID = Field(..., description="ID кандидата")
    status: CandidateStatus = Field(default=CandidateStatus.PENDING, description="Статус кандидата по вакансии")


class VacancyCandidateCreate(VacancyCandidateBase):
    """Схема для создания связи"""
    pass


class VacancyCandidateUpdate(BaseModel):
    """Схема для обновления статуса связи"""
    status: CandidateStatus = Field(..., description="Новый статус кандидата по вакансии")


class VacancyCandidateResponse(VacancyCandidateBase):
    """Схема для ответа API"""
    id: UUID
    assigned_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CandidateWithStatus(BaseModel):
    """Кандидат с его статусом по конкретной вакансии"""
    id: UUID
    name: str
    surname: str
    status: CandidateStatus
    assigned_at: datetime


class VacancyWithCandidates(VacancyResponse):
    """Вакансия со списком кандидатов и их статусами"""
    candidates: List[CandidateWithStatus] = []


class VacancyListResponse(BaseModel):
    """Пагинированный список вакансий"""
    items: list[VacancyResponse]
    total: int
    page: int
    size: int
    pages: int


class CandidateListResponse(BaseModel):
    items: list[CandidateResponse]
    total: int
    page: int
    size: int
    pages: int


class VacancyCandidateListResponse(BaseModel):
    vacancy_id: UUID
    vacancy_name: str
    candidates: list[CandidateWithStatus]
    total: int
