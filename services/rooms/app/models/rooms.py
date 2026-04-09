from sqlalchemy import Column, String, Text, Integer, Float, Boolean, DateTime, ForeignKey, Enum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum
from ..database.session import Base


class Room(Base):
    __tablename__ = "rooms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    interviewer_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    vacancy_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    link = Column(String(255), nullable=False, unique=True, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(50), default="created")

    metrics = relationship("RoomMetric", back_populates="room", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="room", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="room", cascade="all, delete-orphan")
    codes = relationship("Code", back_populates="room", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_rooms_candidate", "candidate_id"),
        Index("idx_rooms_interviewer", "interviewer_id"),
        Index("idx_rooms_vacancy", "vacancy_id"),
        Index("idx_rooms_status", "status"),
        Index("idx_rooms_created_at", "created_at"),
    )


class Metric(Base):
    __tablename__ = "metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True, index=True)
    scale_from = Column(Integer, nullable=False, default=0)
    scale_to = Column(Integer, nullable=False, default=10)
    visible = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Связи
    rooms = relationship("RoomMetric", back_populates="metric", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_metrics_name", "name"),
        Index("idx_metrics_visible", "visible"),
    )


class RoomMetric(Base):
    __tablename__ = "room_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    metric_id = Column(UUID(as_uuid=True), ForeignKey("metrics.id", ondelete="CASCADE"), nullable=False)
    room_id = Column(UUID(as_uuid=True), ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    result = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Связи
    metric = relationship("Metric", back_populates="rooms")
    room = relationship("Room", back_populates="metrics")

    __table_args__ = (
        Index("idx_room_metrics_room", "room_id"),
        Index("idx_room_metrics_metric", "metric_id"),
        Index("idx_room_metrics_unique", "metric_id", "room_id", unique=True),
    )


class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_id = Column(UUID(as_uuid=True), ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False, index=True)
    text_body = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Связи
    room = relationship("Room", back_populates="feedbacks")

    __table_args__ = (
        Index("idx_feedbacks_room", "room_id"),
    )


class Note(Base):
    __tablename__ = "notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_id = Column(UUID(as_uuid=True), ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False, index=True)
    note_body = Column(Text, nullable=False)
    time_offset = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Связи
    room = relationship("Room", back_populates="notes")

    __table_args__ = (
        Index("idx_notes_room", "room_id"),
    )


class Code(Base):
    __tablename__ = "codes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_id = Column(UUID(as_uuid=True), ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False, index=True)
    code_body = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Связи
    room = relationship("Room", back_populates="codes")

    __table_args__ = (
        Index("idx_codes_room", "room_id"),
    )