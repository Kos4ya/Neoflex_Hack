# app/schemas/session.py
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import Optional, List, Any, Dict
from app.core.constants import SessionStatus, Language, MetricName, Severity


# ========== Session Schemas ==========

class SessionCreate(BaseModel):
    """Создание сессии"""
    vacancy_id: UUID
    candidate_id: UUID
    interviewer_id: UUID
    language: Language = Language.PYTHON
    scheduled_start_at: datetime
    scheduled_end_at: datetime


class SessionUpdate(BaseModel):
    """Обновление сессии"""
    status: Optional[SessionStatus] = None
    language: Optional[Language] = None
    scheduled_start_at: Optional[datetime] = None
    scheduled_end_at: Optional[datetime] = None


class SessionResponse(BaseModel):
    """Ответ с данными сессии"""
    id: UUID
    vacancy_id: UUID
    candidate_id: UUID
    interviewer_id: UUID
    manager_id: Optional[UUID] = None
    status: SessionStatus
    language: Language
    scheduled_start_at: datetime
    scheduled_end_at: datetime
    actual_started_at: Optional[datetime] = None
    actual_ended_at: Optional[datetime] = None
    paused_at: Optional[datetime] = None
    total_paused_duration_seconds: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SessionAction(BaseModel):
    """Действие над сессией"""
    action: str  # start, pause, resume, complete, cancel


# ========== Code Schemas ==========

class CodeUpdate(BaseModel):
    """Обновление кода"""
    code: str
    timestamp_ms: int = Field(..., ge=0, description="Миллисекунды от начала интервью")


class CodeVersion(BaseModel):
    """Версия кода"""
    version: int
    code: str
    timestamp_ms: int
    created_at: datetime


class CodeResponse(BaseModel):
    """Текущий код"""
    session_id: UUID
    code: str
    version: int
    updated_at: datetime


class CodeHistoryResponse(BaseModel):
    """История версий кода"""
    session_id: UUID
    versions: List[CodeVersion]
    total_versions: int


# ========== Note Schemas ==========

class NoteCreate(BaseModel):
    """Создание заметки"""
    content: str = Field(..., min_length=1, max_length=2000)
    timestamp_ms: int = Field(..., ge=0, description="Миллисекунды от начала интервью")


class NoteResponse(BaseModel):
    """Ответ с заметкой"""
    id: UUID
    session_id: UUID
    interviewer_id: UUID
    timestamp_ms: int
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


# ========== Metric Schemas ==========

class MetricCreate(BaseModel):
    """Создание метрики (автоматическое)"""
    metric_name: MetricName
    timestamp_ms: int
    metric_value: Dict[str, Any]
    severity: Severity = Severity.INFO


class MetricResponse(BaseModel):
    """Ответ с метрикой"""
    id: UUID
    session_id: UUID
    metric_name: str
    timestamp_ms: int
    metric_value: Optional[Dict[str, Any]]
    severity: str
    created_at: datetime

    class Config:
        from_attributes = True


class MetricsSummary(BaseModel):
    """Сводка по метрикам сессии"""
    session_id: UUID
    total_metrics: int
    warnings_count: int
    critical_count: int
    metrics_by_type: Dict[str, int]
    insights: List[str]


# ========== Resolution Schemas ==========

class ResolutionCreate(BaseModel):
    """Установка резолюции"""
    decision: str = Field(..., pattern="^(passed|failed)$")
    reason: Optional[str] = None


class ResolutionResponse(BaseModel):
    """Ответ с резолюцией"""
    session_id: UUID
    decision: str
    reason: Optional[str]
    set_by: UUID
    set_at: datetime