from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Index, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from schemas.vacancies import CandidateStatus
from database.session import Base


class Vacancy(Base):
    __tablename__ = "vacancies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    candidates_link = relationship("VacancyCandidate", back_populates="vacancy", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_vacancies_name", "name"),
    )


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    surname = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    vacancies_link = relationship("VacancyCandidate", back_populates="candidate", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_candidates_name_surname", "name", "surname"),
    )


class VacancyCandidate(Base):
    __tablename__ = "vacancy_candidates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vacancy_id = Column(UUID(as_uuid=True), ForeignKey("vacancies.id", ondelete="CASCADE"), nullable=False)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum(CandidateStatus), nullable=False, default=CandidateStatus.PENDING)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Связи
    vacancy = relationship("Vacancy", back_populates="candidates_link")
    candidate = relationship("Candidate", back_populates="vacancies_link")

    # Уникальная пара (вакансия, кандидат) - один кандидат не может быть назначен на вакансию дважды
    __table_args__ = (
        Index("idx_vacancy_candidate", "vacancy_id", "candidate_id", unique=True),
        Index("idx_vacancy_candidate_status", "vacancy_id", "status"),
    )