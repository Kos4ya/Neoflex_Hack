from pydantic import BaseModel, Field, ConfigDict, computed_field
from datetime import datetime
from uuid import UUID
from typing import Optional, List
from enum import Enum


class RoomStatusEnum(str, Enum):
    """Статусы комнаты"""
    CREATED = "created"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class RoomStartRequest(BaseModel):
    """Запрос на начало интервью"""
    started_at: Optional[datetime] = Field(None, description="Время начала (опционально, по умолчанию сейчас)")


class RoomCompleteRequest(BaseModel):
    """Запрос на завершение интервью"""
    finished_at: Optional[datetime] = Field(None, description="Время окончания (опционально, по умолчанию сейчас)")


class RoomDurationResponse(BaseModel):
    """Ответ с длительностью интервью"""
    room_id: UUID
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    duration_seconds: int
    duration_minutes: float
    status: str


class RoomStatusUpdate(BaseModel):
    """Обновление статуса комнаты"""
    status: RoomStatusEnum


class RoomBase(BaseModel):
    """Базовые поля комнаты"""
    # candidate_id: UUID = Field(..., description="ID кандидата")
    # interviewer_id: UUID = Field(..., description="ID интервьюера")
    vacancy_id: UUID = Field(..., description="ID вакансии")


class RoomCreate(RoomBase):
    """Схема для создания комнаты"""
    pass


class RoomUpdate(BaseModel):
    """Схема для обновления комнаты"""
    candidate_id: Optional[UUID] = None
    interviewer_id: Optional[UUID] = None
    vacancy_id: Optional[UUID] = None


class RoomResponse(RoomBase):
    """Схема для ответа API"""
    id: UUID
    link: str
    status: str = Field(default="created", description="Статус комнаты: created, active, completed, cancelled")

    created_at: datetime
    updated_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RoomWithDetails(RoomResponse):
    """Комната со всеми связанными данными"""
    metrics: List["RoomMetricResponse"] = []
    feedbacks: List["FeedbackResponse"] = []
    notes: List["NoteResponse"] = []
    codes: List["CodeResponse"] = []


class MetricBase(BaseModel):
    """Базовые поля метрики"""
    name: str = Field(..., min_length=1, max_length=255)
    scale_from: int = Field(default=0, ge=0, le=100)
    scale_to: int = Field(default=10, ge=1, le=100)
    visible: bool = Field(default=True)

class MetricCreate(MetricBase):
    """Схема для создания метрики"""
    pass


class MetricUpdate(BaseModel):
    """Схема для обновления метрики"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    scale_from: Optional[int] = Field(None, ge=0, le=100)
    scale_to: Optional[int] = Field(None, ge=1, le=100)
    visible: Optional[bool] = None

class MetricResponse(MetricBase):
    """Схема для ответа API"""
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RoomMetricBase(BaseModel):
    """Базовые поля связи комната-метрика"""
    # metric_id: UUID = Field(..., description="ID метрики")
    # room_id: UUID = Field(..., description="ID комнаты")
    result: Optional[float] = Field(None, description="Результат оценки")


class RoomMetricCreate(RoomMetricBase):
    pass


class RoomMetricUpdate(BaseModel):
    """Обновление результата метрики"""
    result: Optional[float] = None


class RoomMetricResponse(RoomMetricBase):
    """Ответ со связью комнаты и метрики"""
    id: UUID
    room_id: UUID
    metric_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RoomMetricWithDetails(RoomMetricResponse):
    """Связь с деталями метрики"""
    metric: MetricResponse


class FeedbackBase(BaseModel):
    """Базовые поля фидбека"""
    text_body: str = Field(..., min_length=1, max_length=5000)


class FeedbackCreate(FeedbackBase):
    pass


class FeedbackUpdate(BaseModel):
    """Обновление фидбека"""
    text_body: Optional[str] = Field(None, min_length=1, max_length=5000)


class FeedbackResponse(FeedbackBase):
    """Ответ с данными фидбека"""
    id: UUID
    room_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NoteBase(BaseModel):
    """Базовые поля заметки"""
    note_body: str = Field(..., min_length=1, max_length=5000)


class NoteCreate(NoteBase):
    pass


class NoteUpdate(BaseModel):
    """Обновление заметки"""
    note_body: Optional[str] = Field(None, min_length=1, max_length=5000)


class NoteResponse(NoteBase):
    """Ответ с данными заметки"""
    id: UUID
    room_id: UUID
    time_offset: Optional[int] = Field(None, description="Время от начала интервью (секунды)")
    timecode: Optional[str] = Field(None, description="Форматированное время MM:SS")
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    @computed_field
    @property
    def formatted_time(self) -> str:
        """Форматирует секунды в MM:SS"""
        if self.time_offset is None:
            return "00:00"
        minutes = self.time_offset // 60
        seconds = self.time_offset % 60
        return f"{minutes:02d}:{seconds:02d}"



class CodeBase(BaseModel):
    """Базовые поля кода"""
    code_body: str = Field(..., description="Код, написанный кандидатом")


class CodeCreate(CodeBase):
    pass


class CodeUpdate(BaseModel):
    """Обновление кода"""
    code_body: Optional[str] = None


class CodeResponse(CodeBase):
    """Ответ с данными кода"""
    id: UUID
    room_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RoomListResponse(BaseModel):
    items: List[RoomResponse]
    total: int
    page: int
    size: int
    pages: int


class MetricListResponse(BaseModel):
    items: List[MetricResponse]
    total: int
    page: int
    size: int
    pages: int


class GenerateLinkResponse(BaseModel):
    """Ответ с сгенерированной ссылкой"""
    room_id: UUID
    link: str


class BulkAssignMetrics(BaseModel):
    """Массовое назначение метрик комнате"""
    metric_ids: List[UUID]