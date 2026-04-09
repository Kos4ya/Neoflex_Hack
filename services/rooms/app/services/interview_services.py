from typing import Optional, List, Tuple
from uuid import UUID
from datetime import datetime

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.interview import Interview, InterviewStatus
from app.schemas.interview import InterviewCreate, InterviewUpdate


class InterviewService:
    """Сервис для работы с интервью"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_interview(self, data: InterviewCreate) -> Interview:
        """Создание нового интервью"""
        interview = Interview(
            room_id=data.room_id,
            interviewer_id=data.interviewer_id,
            candidate_id=data.candidate_id,
            vacancy_id=data.vacancy_id,
            scheduled_at=data.scheduled_at,
            status=InterviewStatus.SCHEDULED
        )

        self.db.add(interview)
        await self.db.flush()
        return interview

    async def get_interview(self, interview_id: UUID) -> Optional[Interview]:
        """Получение интервью по ID"""
        result = await self.db.execute(
            select(Interview).where(Interview.id == interview_id)
        )
        return result.scalar_one_or_none()

    async def list_interviews(
            self,
            skip: int = 0,
            limit: int = 100,
            interviewer_id: Optional[UUID] = None,
            candidate_id: Optional[UUID] = None,
            status: Optional[InterviewStatus] = None,
            room_id: Optional[UUID] = None,
    ) -> Tuple[List[Interview], int]:
        """Получение списка интервью с фильтрацией"""
        query = select(Interview)
        count_query = select(func.count(Interview.id))

        conditions = []

        if interviewer_id:
            conditions.append(Interview.interviewer_id == interviewer_id)
        if candidate_id:
            conditions.append(Interview.candidate_id == candidate_id)
        if status:
            conditions.append(Interview.status == status)
        if room_id:
            conditions.append(Interview.room_id == room_id)

        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))

        # Общее количество
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Записи с пагинацией
        query = query.order_by(Interview.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        interviews = result.scalars().all()

        return list(interviews), total

    async def update_interview(
            self,
            interview_id: UUID,
            data: InterviewUpdate
    ) -> Optional[Interview]:
        """Обновление интервью"""
        interview = await self.get_interview(interview_id)
        if not interview:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(interview, field, value)

        await self.db.flush()
        return interview

    async def delete_interview(self, interview_id: UUID) -> bool:
        """Удаление интервью"""
        interview = await self.get_interview(interview_id)
        if not interview:
            return False

        await self.db.delete(interview)
        await self.db.flush()
        return True