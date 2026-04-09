from uuid import UUID
from fastapi import APIRouter, status, Depends, HTTPException

from .base import get_room_service
from ..services.room_service import RoomService
from ..schemas.rooms import (
    RoomMetricCreate,
    RoomMetricUpdate,
    RoomMetricResponse,
    RoomMetricWithDetails,
    BulkAssignMetrics,
)

router = APIRouter(prefix="/rooms/{room_id}/metrics", tags=["Room Metrics"])


@router.get("/", response_model=list[RoomMetricWithDetails])
async def get_room_metrics(
    room_id: UUID,
    service: RoomService = Depends(get_room_service),
):
    """Получить все метрики комнаты"""
    room_metrics = await service.get_room_metrics(room_id)
    if not room_metrics:
        raise HTTPException(status_code=404, detail="Room not found")
    return room_metrics


@router.post("/{metric_id}", response_model=RoomMetricResponse, status_code=status.HTTP_201_CREATED)
async def assign_metric_to_room(
    room_id: UUID,
    metric_id: UUID,
    metric_data: RoomMetricCreate = None,
    service: RoomService = Depends(get_room_service),
):
    """Назначить метрику комнате (с опциональным результатом)"""
    result_value = metric_data.result if metric_data else None

    room_metric = await service.assign_metric_to_room(
        room_id=room_id,
        metric_id=metric_id,
        result=result_value
    )
    if not room_metric:
        raise HTTPException(status_code=400, detail="Room or Metric not found, or metric already assigned")

    await service.db.commit()
    await service.db.refresh(room_metric)
    return room_metric


@router.post("/bulk", response_model=dict)
async def bulk_assign_metrics_to_room(
    room_id: UUID,
    data: BulkAssignMetrics,
    service: RoomService = Depends(get_room_service),
):
    """Массовое назначение метрик комнате"""
    result = await service.bulk_assign_metrics_to_room(room_id, data.metric_ids)
    if result.get("error") == "room_not_found":
        raise HTTPException(status_code=404, detail="Room not found")

    await service.db.commit()
    return result


@router.patch("/{metric_id}", response_model=RoomMetricResponse)
async def update_room_metric_result(
    room_id: UUID,
    metric_id: UUID,
    metric_data: RoomMetricUpdate,
    service: RoomService = Depends(get_room_service),
):
    """Обновить результат метрики в комнате"""
    if metric_data.result is None:
        raise HTTPException(status_code=400, detail="Result is required")

    room_metric = await service.update_room_metric_result(
        room_id=room_id,
        metric_id=metric_id,
        result=metric_data.result
    )
    if not room_metric:
        raise HTTPException(status_code=404, detail="Room metric not found")

    await service.db.commit()
    await service.db.refresh(room_metric)
    return room_metric


@router.delete("/{metric_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_metric_from_room(
    room_id: UUID,
    metric_id: UUID,
    service: RoomService = Depends(get_room_service),
):
    """Удалить метрику из комнаты"""
    deleted = await service.remove_metric_from_room(room_id, metric_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Room metric not found")
    await service.db.commit()