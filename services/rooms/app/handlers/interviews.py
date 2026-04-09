from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Query, status, Depends, HTTPException

from ..database.session import get_db
from ..services.interview_services import InterviewService
from ..schemas.interview import (
    InterviewCreate,
    InterviewUpdate,
    InterviewResponse,
    InterviewListResponse,
    InterviewStatusEnum,
)
from ..models.interview import InterviewStatus

router = APIRouter(prefix="/interviews", tags=["Interviews"])


async def get_interview_service(db=Depends(get_db)):
    return InterviewService(db)


@router.post("/", response_model=InterviewResponse, status_code=status.HTTP_201_CREATED)
async def create_interview(
        data: InterviewCreate,
        service: InterviewService = Depends(get_interview_service),
):
    """Создание интервью"""
    interview = await service.create_interview(data)
    await service.db.commit()
    await service.db.refresh(interview)
    return interview


@router.get("/", response_model=InterviewListResponse)
async def list_interviews(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=500),
        interviewer_id: Optional[UUID] = None,
        candidate_id: Optional[UUID] = None,
        status: Optional[InterviewStatusEnum] = None,
        room_id: Optional[UUID] = None,
        service: InterviewService = Depends(get_interview_service),
):
    """Список интервью с фильтрацией"""
    db_status = InterviewStatus(status.value) if status else None

    interviews, total = await service.list_interviews(
        skip=skip,
        limit=limit,
        interviewer_id=interviewer_id,
        candidate_id=candidate_id,
        status=db_status,
        room_id=room_id,
    )

    return InterviewListResponse(
        items=interviews,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{interview_id}", response_model=InterviewResponse)
async def get_interview(
        interview_id: UUID,
        service: InterviewService = Depends(get_interview_service),
):
    """Получение интервью по ID"""
    interview = await service.get_interview(interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    return interview


@router.put("/{interview_id}", response_model=InterviewResponse)
async def update_interview(
        interview_id: UUID,
        data: InterviewUpdate,
        service: InterviewService = Depends(get_interview_service),
):
    """Обновление интервью"""
    interview = await service.update_interview(interview_id, data)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    await service.db.commit()
    await service.db.refresh(interview)
    return interview


@router.delete("/{interview_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_interview(
        interview_id: UUID,
        service: InterviewService = Depends(get_interview_service),
):
    """Удаление интервью"""
    deleted = await service.delete_interview(interview_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Interview not found")

    await service.db.commit()