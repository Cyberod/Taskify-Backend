from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship
import datetime
from datetime import timezone

def utc_now():
    """Returns the current UTC datetime."""
    return datetime.now(timezone.utc)


from app.db.session import Base

class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)  # Size in bytes
    task_id = Column(Integer, ForeignKey("tasks.id"))

    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    # Relationships
    task = relationship("Task", back_populates="attachments")