from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Query, status, Depends, HTTPException

from .base import get_room_service
from ..services.room_service import RoomService
from ..schemas.rooms import MetricCreate, MetricUpdate, MetricResponse

router = APIRouter(prefix="/rooms/metrics", tags=["Metrics"])


@router.get("/", response_model=List[MetricResponse])
async def list_metrics(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    visible_only: bool = Query(False, description="Только видимые метрики"),
    name: Optional[str] = Query(None, description="Поиск по имени"),
    service: RoomService = Depends(get_room_service),
):
    """Получение списка всех метрик (справочник)"""
    metrics = await service.list_metrics(
        skip=skip,
        limit=limit,
        visible_only=visible_only,
        name=name
    )
    return metrics


@router.post("/", response_model=MetricResponse, status_code=status.HTTP_201_CREATED)
async def create_metric(
    metric_data: MetricCreate,
    service: RoomService = Depends(get_room_service),
):
    """Создание новой метрики"""
    metric = await service.create_metric(metric_data)
    await service.db.commit()
    await service.db.refresh(metric)
    return metric


@router.get("/{metric_id}", response_model=MetricResponse)
async def get_metric(
    metric_id: UUID,
    service: RoomService = Depends(get_room_service),
):
    """Получение метрики по ID"""
    metric = await service.get_metric(metric_id)
    if not metric:
        raise HTTPException(status_code=404, detail="Metric not found")
    return metric


@router.put("/{metric_id}", response_model=MetricResponse)
async def update_metric(
    metric_id: UUID,
    metric_data: MetricUpdate,
    service: RoomService = Depends(get_room_service),
):
    """Обновление метрики"""
    metric = await service.update_metric(metric_id, metric_data)
    if not metric:
        raise HTTPException(status_code=404, detail="Metric not found")
    await service.db.commit()
    await service.db.refresh(metric)
    return metric


@router.delete("/{metric_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_metric(
    metric_id: UUID,
    service: RoomService = Depends(get_room_service),
):
    """Удаление метрики"""
    deleted = await service.delete_metric(metric_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Metric not found")
    await service.db.commit()