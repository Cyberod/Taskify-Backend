from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
import datetime
from datetime import timezone

from app.db.session import Base
from app.models.user import project_members

def utc_now():
    return datetime.now(timezone.utc)


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    deadline = Column(DateTime, nullable=True)
    completion_percentage = Column(Float, default=0.0)
    is_completed = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))

    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    # Relationships
    owner = relationship("User", back_populates="owned_projects")
    members = relationship("User", secondary=project_members, back_populates="projects")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="project")