import uuid
from sqlalchemy import Column, String, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from ..database.session import Base


class Room(Base):
    __tablename__ = "rooms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vacancy_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Уникальная ссылка для входа
    link = Column(String(255), nullable=False, unique=True, index=True)
    language = Column(String(255), nullable=False)

    status = Column(String(50), default="created", index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Связи
    interview = relationship(
        "Interview",
        back_populates="room",
        uselist=False,  # 1:1
        cascade="all, delete-orphan"
    )
    metrics = relationship("RoomMetric", back_populates="room", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="room", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="room", cascade="all, delete-orphan")
    codes = relationship("Code", back_populates="room", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_rooms_vacancy", "vacancy_id"),
        Index("idx_rooms_status", "status"),
        Index("idx_rooms_created_at", "created_at"),
        Index("idx_rooms_link", "link"),
    )

    @property
    def is_active(self) -> bool:
        """Активна ли комната для WebSocket соединений"""
        return self.status in ["active", "created"]