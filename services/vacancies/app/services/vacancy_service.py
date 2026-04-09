from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from uuid import UUID
from typing import List, Optional

from ..models.vacancies import Vacancy, Candidate, VacancyCandidate
from ..schemas.vacancies import (
    VacancyCreate, VacancyUpdate,
    CandidateCreate, CandidateUpdate,
    CandidateStatus
)


class VacancyService:
    """Сервис для работы с вакансиями и кандидатами"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_vacancies(
            self,
            skip: int = 0,
            limit: int = 100,
            name: Optional[str] = None
    ) -> List[Vacancy]:
        """Список вакансий с фильтрацией"""
        query = select(Vacancy)
        if name:
            query = query.where(Vacancy.name.ilike(f"%{name}%"))
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_vacancy(self, vacancy_id: UUID) -> Optional[Vacancy]:
        """Получение вакансии по ID"""
        result = await self.db.execute(
            select(Vacancy).where(Vacancy.id == vacancy_id)
        )
        return result.scalar_one_or_none()

    async def create_vacancy(self, vacancy_data: VacancyCreate) -> Vacancy:
        """Создание вакансии"""
        vacancy = Vacancy(name=vacancy_data.name)
        self.db.add(vacancy)
        await self.db.flush()
        return vacancy

    async def update_vacancy(
            self,
            vacancy_id: UUID,
            vacancy_data: VacancyUpdate
    ) -> Optional[Vacancy]:
        """Обновление вакансии"""
        vacancy = await self.get_vacancy(vacancy_id)
        if not vacancy:
            return None

        update_data = vacancy_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(vacancy, key, value)

        await self.db.flush()
        return vacancy

    async def delete_vacancy(self, vacancy_id: UUID) -> bool:
        """Удаление вакансии"""
        vacancy = await self.get_vacancy(vacancy_id)
        if not vacancy:
            return False

        await self.db.delete(vacancy)
        await self.db.flush()
        return True


    async def list_candidates(
            self,
            skip: int = 0,
            limit: int = 100,
            name: Optional[str] = None,
            surname: Optional[str] = None,
            vacancy_id: Optional[UUID] = None
    ) -> List[Candidate]:
        """Список кандидатов с фильтрацией"""
        if vacancy_id:
            query = select(Candidate).join(
                VacancyCandidate, Candidate.id == VacancyCandidate.candidate_id
            ).where(VacancyCandidate.vacancy_id == vacancy_id)
        else:
            query = select(Candidate)

        if name:
            query = query.where(Candidate.name.ilike(f"%{name}%"))
        if surname:
            query = query.where(Candidate.surname.ilike(f"%{surname}%"))

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_candidate(self, candidate_id: UUID) -> Optional[Candidate]:
        """Получение кандидата по ID"""
        result = await self.db.execute(
            select(Candidate).where(Candidate.id == candidate_id)
        )
        return result.scalar_one_or_none()

    async def create_candidate(self, candidate_data: CandidateCreate) -> Candidate:
        """Создание кандидата"""
        candidate = Candidate(
            name=candidate_data.name,
            surname=candidate_data.surname
        )
        self.db.add(candidate)
        await self.db.flush()
        return candidate

    async def update_candidate(
            self,
            candidate_id: UUID,
            candidate_data: CandidateUpdate
    ) -> Optional[Candidate]:
        """Обновление кандидата"""
        candidate = await self.get_candidate(candidate_id)
        if not candidate:
            return None

        update_data = candidate_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(candidate, key, value)

        await self.db.flush()
        return candidate

    async def delete_candidate(self, candidate_id: UUID) -> bool:
        """Удаление кандидата"""
        candidate = await self.get_candidate(candidate_id)
        if not candidate:
            return False

        await self.db.delete(candidate)
        await self.db.flush()
        return True


    async def get_vacancy_candidates(
            self,
            vacancy_id: UUID
    ) -> List[dict]:
        """Получение всех кандидатов по вакансии с их статусами"""
        result = await self.db.execute(
            select(Candidate, VacancyCandidate.status, VacancyCandidate.assigned_at)
            .join(VacancyCandidate, Candidate.id == VacancyCandidate.candidate_id)
            .where(VacancyCandidate.vacancy_id == vacancy_id)
        )

        return [
            {
                "id": c.id,
                "name": c.name,
                "surname": c.surname,
                "status": status,
                "assigned_at": assigned_at
            }
            for c, status, assigned_at in result.all()
        ]

    async def assign_candidate_to_vacancy(
            self,
            vacancy_id: UUID,
            candidate_id: UUID
    ) -> Optional[dict]:
        """Назначение кандидата на вакансию"""
        vacancy = await self.get_vacancy(vacancy_id)
        candidate = await self.get_candidate(candidate_id)

        if not vacancy or not candidate:
            return None

        # Проверяем, не назначен ли уже
        existing = await self.db.execute(
            select(VacancyCandidate).where(
                VacancyCandidate.vacancy_id == vacancy_id,
                VacancyCandidate.candidate_id == candidate_id
            )
        )
        if existing.scalar_one_or_none():
            return {"error": "already_assigned"}

        assignment = VacancyCandidate(
            vacancy_id=vacancy_id,
            candidate_id=candidate_id
        )
        self.db.add(assignment)
        await self.db.commit()

        return {
            "vacancy_id": vacancy_id,
            "candidate_id": candidate_id,
            "message": "assigned"
        }

    async def remove_candidate_from_vacancy(
            self,
            vacancy_id: UUID,
            candidate_id: UUID
    ) -> bool:
        """Удаление кандидата с вакансии"""
        result = await self.db.execute(
            select(VacancyCandidate).where(
                VacancyCandidate.vacancy_id == vacancy_id,
                VacancyCandidate.candidate_id == candidate_id
            )
        )
        assignment = result.scalar_one_or_none()
        if not assignment:
            return False

        await self.db.delete(assignment)
        await self.db.flush()
        return True

    async def change_candidate_status(
            self,
            vacancy_id: UUID,
            candidate_id: UUID,
            status: str
    ) -> Optional[dict]:
        """Смена статуса кандидата по вакансии"""
        if status not in [s.value for s in CandidateStatus]:
            return {"error": "invalid_status"}

        result = await self.db.execute(
            select(VacancyCandidate).where(
                VacancyCandidate.vacancy_id == vacancy_id,
                VacancyCandidate.candidate_id == candidate_id
            )
        )
        assignment = result.scalar_one_or_none()
        if not assignment:
            return None

        assignment.status = status
        await self.db.flush()

        return {
            "vacancy_id": vacancy_id,
            "candidate_id": candidate_id,
            "status": status
        }
