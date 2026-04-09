from uuid import UUID
from fastapi import APIRouter, status, Depends, HTTPException

from .base import get_room_service
from ..services.room_service import RoomService
from ..schemas.rooms import FeedbackCreate, FeedbackUpdate, FeedbackResponse

router = APIRouter(prefix="/rooms", tags=["Feedbacks"])


@router.get("/{room_id}/feedbacks", response_model=list[FeedbackResponse])
async def get_room_feedbacks(
    room_id: UUID,
    service: RoomService = Depends(get_room_service),
):
    """Получить все фидбеки комнаты"""
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
    """Создать фидбек в комнате"""
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
    """Обновить фидбек"""
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
    """Удалить фидбек"""
    deleted = await service.delete_feedback(feedback_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Feedback not found")
    await service.db.commit()