from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
import datetime
from datetime import timezone

from app.db.session import Base

def utc_now():
    """Returns the current UTC datetime."""
    return datetime.now(timezone.utc)


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    author_id = Column(Integer, ForeignKey("users.id"))

    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    # Relationships
    task = relationship("Task", back_populates="comments")
    author = relationship("User", back_populates="comments")