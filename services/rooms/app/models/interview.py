import enum
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from ..database.session import Base


class InterviewStatus(str, enum.Enum):
    """Статусы интервью"""
    SCHEDULED = "scheduled"  # Запланировано
    PENDING_FEEDBACK = "pending_feedback"  # Проведено, ожидает фидбек
    COMPLETED = "completed"  # С фидбеком (завершено)


class Interview(Base):
    __tablename__ = "interviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    room_id = Column(
        UUID(as_uuid=True),
        ForeignKey("rooms.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,  # Обеспечивает связь 1:1
        index=True
    )

    # Участники (внешние сервисы)
    interviewer_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    candidate_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    candidate_token = Column(String, nullable=False, unique=True, index=True)
    # Временные метки
    scheduled_at = Column(DateTime(timezone=True), nullable=True, index=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)

    # Статус интервью
    status = Column(
        Enum(InterviewStatus, name="interview_status"),
        nullable=False,
        default=InterviewStatus.SCHEDULED,
        index=True
    )

    # Связь с фидбеком (может быть несколько, но основной - через этот id)
    primary_feedback_id = Column(
        UUID(as_uuid=True),
        ForeignKey("feedbacks.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Связи
    room = relationship("Room", back_populates="interview", uselist=False)  # 1:1
    primary_feedback = relationship("Feedback", foreign_keys=[primary_feedback_id], post_update=True)

    __table_args__ = (
        Index("idx_interviews_interviewer", "interviewer_id"),
        Index("idx_interviews_candidate", "candidate_id"),
        Index("idx_interviews_status", "status"),
        Index("idx_interviews_scheduled", "scheduled_at"),
        Index("idx_interviews_room", "room_id"),
    )