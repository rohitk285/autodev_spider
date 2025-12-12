import uuid
from sqlalchemy import Column, Boolean, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID

from .database import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    description = Column(String, index=True, nullable=False)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
