from fastapi import APIRouter, Query
from typing import List, Optional
from uuid import UUID
from app.schemas.session import MetricResponse, MetricsSummary
from app.core.constants import MetricName, Severity

router = APIRouter(prefix="/sessions/{session_id}/metrics", tags=["Metrics"])


@router.get("/", response_model=List[MetricResponse])
async def get_session_metrics(
    session_id: UUID,
    metric_name: Optional[MetricName] = None,
    severity: Optional[Severity] = None,
    limit: int = Query(100, ge=1, le=500),
):
    """Получить все метрики сессии"""
    pass


@router.get("/summary", response_model=MetricsSummary)
async def get_metrics_summary(session_id: UUID):
    """Получить сводку по метрикам"""
    pass


@router.post("/detect-inactivity")
async def detect_inactivity(session_id: UUID):
    """Запустить детекцию неактивности кандидата"""
    pass


@router.post("/detect-paste")
async def detect_paste(session_id: UUID, code_size: int):
    """Запустить детекцию вставки кода"""
    pass