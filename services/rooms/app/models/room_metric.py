import uuid
from sqlalchemy import Column, Float, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from ..database.session import Base


class RoomMetric(Base):
    __tablename__ = "room_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    metric_id = Column(
        UUID(as_uuid=True),
        ForeignKey("metrics.id", ondelete="CASCADE"),
        nullable=False
    )
    room_id = Column(
        UUID(as_uuid=True),
        ForeignKey("rooms.id", ondelete="CASCADE"),
        nullable=False
    )
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