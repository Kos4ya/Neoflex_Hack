"""Модель фидбека с поддержкой primary feedback для интервью"""

import uuid
from sqlalchemy import Column, Text, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from ..database.session import Base


class Feedback(Base):
    __tablename__ = "feedbacks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_id = Column(
        UUID(as_uuid=True),
        ForeignKey("rooms.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    author_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    # Текст фидбека
    text_body = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Связи
    room = relationship("Room", back_populates="feedbacks")

    # Связь с интервью (обратная)
    interview = relationship(
        "Interview",
        foreign_keys="Interview.primary_feedback_id",
        back_populates="primary_feedback",
        uselist=False
    )

    __table_args__ = (
        Index("idx_feedbacks_room", "room_id"),
    )