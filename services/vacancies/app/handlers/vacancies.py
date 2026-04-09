from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas.vacancies import VacancyCreate, VacancyUpdate, VacancyResponse, CandidateResponse, CandidateCreate, \
    CandidateUpdate, CandidateWithStatus
from ..database.session import get_db
from ..services.vacancy_service import VacancyService
from uuid import UUID

router = APIRouter()


async def get_vacancy_service(db: AsyncSession = Depends(get_db)):
    return VacancyService(db)

@router.post("/vacancies", response_model=VacancyResponse)
async def create_vacancy(data: VacancyCreate, service: VacancyService = Depends(get_vacancy_service)):
    vacancy = await service.create_vacancy(data)
    return vacancy


@router.get("/vacancies", response_model=List[VacancyResponse])
async def get_vacancies(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=500),
        name: Optional[str] = None,
        service: VacancyService = Depends(get_vacancy_service),
):
    """Список вакансий"""
    vacancies = await service.list_vacancies(
        skip=skip,
        limit=limit,
        name=name,
    )
    return vacancies


@router.put("/vacancies/{vacancy_id}", response_model=VacancyResponse)
async def update_vacancy(
    vacancy_id: UUID,
    vacancy_data: VacancyUpdate,
    service: VacancyService = Depends(get_vacancy_service),
):
    """Обновление вакансии"""
    vacancy = await service.update_vacancy(vacancy_id, vacancy_data)
    if not vacancy:
        raise HTTPException(status_code=404, detail="Vacancy not found")
    return vacancy


@router.get("/vacancies/{vacancy_id}", response_model=VacancyResponse)
async def get_vacancy(
    vacancy_id: UUID,
    service: VacancyService = Depends(get_vacancy_service),
):
    """Получение вакансии по ID"""
    vacancy = await service.get_vacancy(vacancy_id)
    if not vacancy:
        raise HTTPException(status_code=404, detail="Vacancy not found")
    return vacancy


@router.delete("/vacancies/{vacancy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vacancy(
    vacancy_id: UUID,
    service: VacancyService = Depends(get_vacancy_service),
):
    """Удаление вакансии"""
    deleted = await service.delete_vacancy(vacancy_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Vacancy not found")


@router.get("/candidates", response_model=List[CandidateResponse])
async def list_candidates(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    name: Optional[str] = None,
    surname: Optional[str] = None,
    vacancy_id: Optional[UUID] = None,
    service: VacancyService = Depends(get_vacancy_service),
):
    """Список кандидатов"""
    candidates = await service.list_candidates(
        skip=skip,
        limit=limit,
        name=name,
        surname=surname,
        vacancy_id=vacancy_id,
    )
    return candidates


@router.get("/candidates/{candidate_id}", response_model=CandidateResponse)
async def get_candidate(
    candidate_id: UUID,
    service: VacancyService = Depends(get_vacancy_service),
):
    """Получение кандидата по ID"""
    candidate = await service.get_candidate(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate


@router.post("/candidates", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
async def create_candidate(
    candidate_data: CandidateCreate,
    service: VacancyService = Depends(get_vacancy_service),
):
    """Создание кандидата"""
    candidate = await service.create_candidate(candidate_data)
    return candidate


@router.put("/candidates/{candidate_id}", response_model=CandidateResponse)
async def update_candidate(
    candidate_id: UUID,
    candidate_data: CandidateUpdate,
    service: VacancyService = Depends(get_vacancy_service),
):
    """Обновление кандидата"""
    candidate = await service.update_candidate(candidate_id, candidate_data)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate


@router.delete("/candidates/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_candidate(
    candidate_id: UUID,
    service: VacancyService = Depends(get_vacancy_service),
):
    """Удаление кандидата"""
    deleted = await service.delete_candidate(candidate_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Candidate not found")


@router.get("/vacancies/{vacancy_id}/candidates", response_model=List[CandidateWithStatus])
async def get_vacancy_candidates(
        vacancy_id: UUID,
        service: VacancyService = Depends(get_vacancy_service),
):
    """Получение всех кандидатов по вакансии с их статусами"""
    vacancy = await service.get_vacancy(vacancy_id)
    if not vacancy:
        raise HTTPException(status_code=404, detail="Vacancy not found")

    candidates = await service.get_vacancy_candidates(vacancy_id)
    return candidates


@router.post("/vacancies/{vacancy_id}/candidates/{candidate_id}", status_code=status.HTTP_201_CREATED)
async def assign_candidate_to_vacancy(
        vacancy_id: UUID,
        candidate_id: UUID,
        service: VacancyService = Depends(get_vacancy_service),
):
    """Назначение кандидата на вакансию"""
    result = await service.assign_candidate_to_vacancy(vacancy_id, candidate_id)

    if result is None:
        raise HTTPException(status_code=404, detail="Vacancy or Candidate not found")

    if result.get("error") == "already_assigned":
        raise HTTPException(status_code=400, detail="Candidate already assigned to this vacancy")

    return {"message": f"Candidate {candidate_id} assigned to vacancy {vacancy_id}"}


@router.delete("/vacancies/{vacancy_id}/candidates/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_candidate_from_vacancy(
    vacancy_id: UUID,
    candidate_id: UUID,
    service: VacancyService = Depends(get_vacancy_service),
):
    """Удаление кандидата с вакансии"""
    removed = await service.remove_candidate_from_vacancy(vacancy_id, candidate_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Assignment not found")


@router.patch("/vacancies/{vacancy_id}/candidates/{candidate_id}/status")
async def change_candidate_status(
        vacancy_id: UUID,
        candidate_id: UUID,
        status: str,
        service: VacancyService = Depends(get_vacancy_service),
):
    """Смена статуса кандидата по вакансии"""
    result = await service.change_candidate_status(vacancy_id, candidate_id, status)

    if result is None:
        raise HTTPException(status_code=404, detail="Assignment not found")

    if result.get("error") == "invalid_status":
        raise HTTPException(
            status_code=400,
            detail="Invalid status. Must be one of: pending, reviewed, invited, rejected, hired"
        )

    return {"message": f"Status for candidate {candidate_id} updated to {status}"}
