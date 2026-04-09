from fastapi import APIRouter, Query, status, Depends, HTTPException
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.services.room_service import RoomService
from app.schemas.rooms import (
    # Room
    RoomCreate, RoomUpdate, RoomResponse, RoomWithDetails,
    RoomListResponse, GenerateLinkResponse, BulkAssignMetrics,
    # Metric
    MetricCreate, MetricUpdate, MetricResponse, MetricListResponse,
    # RoomMetric
    RoomMetricCreate, RoomMetricUpdate, RoomMetricResponse, RoomMetricWithDetails,
    # Feedback
    FeedbackCreate, FeedbackUpdate, FeedbackResponse,
    # Note
    NoteCreate, NoteUpdate, NoteResponse,
    # Code
    CodeCreate, CodeUpdate, CodeResponse, RoomDurationResponse,
)

router = APIRouter(prefix="/rooms", tags=["Rooms"])


async def get_room_service(db: AsyncSession = Depends(get_db)):
    return RoomService(db)


@router.get("/", response_model=List[RoomResponse])
async def list_rooms(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=500),
        candidate_id: Optional[UUID] = None,
        interviewer_id: Optional[UUID] = None,
        vacancy_id: Optional[UUID] = None,
        service: RoomService = Depends(get_room_service),
):
    """Список комнат с фильтрацией"""
    rooms = await service.list_rooms(
        skip=skip,
        limit=limit,
        candidate_id=candidate_id,
        interviewer_id=interviewer_id,
        vacancy_id=vacancy_id,
    )
    return rooms


@router.post("/", response_model=GenerateLinkResponse, status_code=status.HTTP_201_CREATED)
async def create_room(
        room_data: RoomCreate,
        service: RoomService = Depends(get_room_service),
):
    """Создание комнаты"""
    room = await service.create_room(room_data)
    await service.db.commit()
    await service.db.refresh(room)
    return GenerateLinkResponse(room_id=room.id, link=room.link)


@router.get("/metrics", response_model=List[MetricResponse])
async def list_metrics(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=500),
        visible_only: bool = False,
        name: Optional[str] = None,
        service: RoomService = Depends(get_room_service),
):
    """Список метрик с фильтрацией"""
    metrics = await service.list_metrics(
        skip=skip,
        limit=limit,
        visible_only=visible_only,
        name=name,
    )
    return metrics


@router.get("/metrics/{metric_id}", response_model=MetricResponse)
async def get_metric(
        metric_id: UUID,
        service: RoomService = Depends(get_room_service),
):
    """Получение метрики по ID"""
    metric = await service.get_metric(metric_id)
    if not metric:
        raise HTTPException(status_code=404, detail="Metric not found")
    return metric


@router.post("/metrics", response_model=MetricResponse, status_code=status.HTTP_201_CREATED)
async def create_metric(
        metric_data: MetricCreate,
        service: RoomService = Depends(get_room_service),
):
    """Создание метрики"""
    metric = await service.create_metric(metric_data)
    await service.db.commit()
    await service.db.refresh(metric)
    return metric


@router.put("/metrics/{metric_id}", response_model=MetricResponse)
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


@router.delete("/metrics/{metric_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_metric(
        metric_id: UUID,
        service: RoomService = Depends(get_room_service),
):
    """Удаление метрики"""
    deleted = await service.delete_metric(metric_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Metric not found")
    await service.db.commit()



@router.get("/{room_id}", response_model=RoomResponse)
async def get_room(
        room_id: UUID,
        service: RoomService = Depends(get_room_service),
):
    """Получение комнаты по ID"""
    room = await service.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room


@router.get("/by-link/{link}", response_model=RoomResponse)
async def get_room_by_link(
        link: str,
        service: RoomService = Depends(get_room_service),
):
    """Получение комнаты по ссылке"""
    room = await service.get_room_by_link(link)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room


@router.put("/{room_id}", response_model=RoomResponse)
async def update_room(
        room_id: UUID,
        room_data: RoomUpdate,
        service: RoomService = Depends(get_room_service),
):
    """Обновление комнаты"""
    room = await service.update_room(room_id, room_data)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    await service.db.commit()
    await service.db.refresh(room)
    return room


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room(
        room_id: UUID,
        service: RoomService = Depends(get_room_service),
):
    """Удаление комнаты"""
    deleted = await service.delete_room(room_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Room not found")
    await service.db.commit()


@router.get("/{room_id}/details", response_model=RoomWithDetails)
async def get_room_with_details(
        room_id: UUID,
        service: RoomService = Depends(get_room_service),
):
    """Получение комнаты со всеми связанными данными"""
    details = await service.get_room_with_details(room_id)
    if not details:
        raise HTTPException(status_code=404, detail="Room not found")
    return details


@router.post("/{room_id}/start", response_model=RoomResponse)
async def start_room(
        room_id: UUID,
        service: RoomService = Depends(get_room_service),
):
    """
    Начать интервью в комнате.
    Статус меняется с 'created' на 'active', проставляется время старта.
    """
    room = await service.start_room(room_id)
    if not room:
        raise HTTPException(
            status_code=400,
            detail="Cannot start room. Room not found or already active/completed"
        )
    await service.db.commit()
    await service.db.refresh(room)
    return room


@router.post("/{room_id}/complete", response_model=RoomResponse)
async def complete_room(
        room_id: UUID,
        service: RoomService = Depends(get_room_service),
):
    """
    Завершить интервью в комнате.
    Статус меняется с 'active' на 'completed', проставляется время окончания.
    """
    room = await service.complete_room(room_id)
    if not room:
        raise HTTPException(
            status_code=400,
            detail="Cannot complete room. Room not found or not active"
        )
    await service.db.commit()
    await service.db.refresh(room)
    return room


@router.post("/{room_id}/cancel", response_model=RoomResponse)
async def cancel_room(
        room_id: UUID,
        service: RoomService = Depends(get_room_service),
):
    """
    Отменить интервью в комнате.
    Статус меняется на 'cancelled'.
    """
    room = await service.cancel_room(room_id)
    if not room:
        raise HTTPException(
            status_code=400,
            detail="Cannot cancel room. Room not found or already completed"
        )
    await service.db.commit()
    await service.db.refresh(room)
    return room


@router.get("/status/active", response_model=List[RoomResponse])
async def get_active_rooms(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=500),
        interviewer_id: Optional[UUID] = None,
        service: RoomService = Depends(get_room_service),
):
    """
    Получить все активные комнаты (интервью в процессе).
    Можно отфильтровать по интервьюеру.
    """
    rooms = await service.get_active_rooms(
        skip=skip,
        limit=limit,
        interviewer_id=interviewer_id
    )
    return rooms


@router.get("/status/{status}", response_model=List[RoomResponse])
async def get_rooms_by_status(
        status: str,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=500),
        service: RoomService = Depends(get_room_service),
):
    """
    Получить комнаты по статусу.
    Доступные статусы: created, active, completed, cancelled
    """
    valid_statuses = ["created", "active", "completed", "cancelled"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )

    rooms = await service.get_rooms_by_status(
        status=status,
        skip=skip,
        limit=limit
    )
    return rooms


@router.get("/{room_id}/duration", response_model=RoomDurationResponse)
async def get_room_duration(
        room_id: UUID,
        service: RoomService = Depends(get_room_service),
):
    """
    Получить длительность интервью в комнате.
    """
    duration = await service.get_room_duration(room_id)
    if not duration:
        raise HTTPException(status_code=404, detail="Room not found")

    if duration.get("error"):
        raise HTTPException(status_code=400, detail=duration["error"])

    return duration


@router.get("/{room_id}/metrics", response_model=List[RoomMetricWithDetails])
async def get_room_metrics(
        room_id: UUID,
        service: RoomService = Depends(get_room_service),
):
    """Получить все метрики комнаты"""
    room_metrics = await service.get_room_metrics(room_id)
    if not room_metrics:
        raise HTTPException(status_code=404, detail="Room not found")
    return room_metrics


@router.post("/{room_id}/metrics/{metric_id}", response_model=RoomMetricResponse, status_code=status.HTTP_201_CREATED)
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


@router.post("/{room_id}/metrics/bulk", response_model=dict)
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


@router.patch("/{room_id}/metrics/{metric_id}", response_model=RoomMetricResponse)
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


@router.delete("/{room_id}/metrics/{metric_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_metric_from_room(
        room_id: UUID,
        metric_id: UUID,
        service: RoomService = Depends(get_room_service),
):
    deleted = await service.remove_metric_from_room(room_id, metric_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Room metric not found")
    await service.db.commit()


@router.get("/{room_id}/feedbacks", response_model=List[FeedbackResponse])
async def get_room_feedbacks(
        room_id: UUID,
        service: RoomService = Depends(get_room_service),
):
    room = await service.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    feedbacks = await service.get_room_feedbacks(room_id)
    return feedbacks


@router.post("/{room_id}/feedbacks", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def create_feedback(
        room_id: UUID,
        feedback_data: FeedbackCreate,
        service: RoomService = Depends(get_room_service),
):
    feedback = await service.create_feedback(room_id, feedback_data)
    if not feedback:
        raise HTTPException(status_code=404, detail="Room not found")

    await service.db.commit()
    await service.db.refresh(feedback)
    return feedback


@router.put("/feedbacks/{feedback_id}", response_model=FeedbackResponse)
async def update_feedback(
        feedback_id: UUID,
        feedback_data: FeedbackUpdate,
        service: RoomService = Depends(get_room_service),
):
    feedback = await service.update_feedback(feedback_id, feedback_data)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")

    await service.db.commit()
    await service.db.refresh(feedback)
    return feedback


@router.delete("/feedbacks/{feedback_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_feedback(
        feedback_id: UUID,
        service: RoomService = Depends(get_room_service),
):
    deleted = await service.delete_feedback(feedback_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Feedback not found")
    await service.db.commit()


@router.get("/{room_id}/notes", response_model=List[NoteResponse])
async def get_room_notes(
        room_id: UUID,
        service: RoomService = Depends(get_room_service),
):
    room = await service.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    notes = await service.get_room_notes(room_id)
    return notes


@router.post("/{room_id}/notes", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
        room_id: UUID,
        note_data: NoteCreate,
        service: RoomService = Depends(get_room_service),
):
    note = await service.create_note(room_id, note_data)
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
    deleted = await service.delete_note(note_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Note not found")
    await service.db.commit()


@router.get("/{room_id}/codes", response_model=List[CodeResponse])
async def get_room_codes(
        room_id: UUID,
        service: RoomService = Depends(get_room_service),
):
    room = await service.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    codes = await service.get_room_codes(room_id)
    return codes


@router.post("/{room_id}/codes", response_model=CodeResponse, status_code=status.HTTP_201_CREATED)
async def create_code(
        room_id: UUID,
        code_data: CodeCreate,
        service: RoomService = Depends(get_room_service),
):
    code = await service.create_code(room_id, code_data)
    if not code:
        raise HTTPException(status_code=404, detail="Room not found")

    await service.db.commit()
    await service.db.refresh(code)
    return code


@router.put("/codes/{code_id}", response_model=CodeResponse)
async def update_code(
        code_id: UUID,
        code_data: CodeUpdate,
        service: RoomService = Depends(get_room_service),
):
    code = await service.update_code(code_id, code_data)
    if not code:
        raise HTTPException(status_code=404, detail="Code not found")

    await service.db.commit()
    await service.db.refresh(code)
    return code


@router.delete("/codes/{code_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_code(
        code_id: UUID,
        service: RoomService = Depends(get_room_service),
):
    deleted = await service.delete_code(code_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Code not found")
    await service.db.commit()