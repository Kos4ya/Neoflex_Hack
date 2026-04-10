import uuid
from sqlalchemy import Column, Text, DateTime, ForeignKey, Index, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from ..database.session import Base


class Code(Base):
    __tablename__ = "codes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_id = Column(
        UUID(as_uuid=True),
        ForeignKey("rooms.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )
    code_body = Column(Text, nullable=False)
    version = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    room = relationship("Room", back_populates="codes")

    __table_args__ = (
        Index("idx_codes_room", "room_id"),
    )