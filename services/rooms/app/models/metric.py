import uuid
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from ..database.session import Base


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