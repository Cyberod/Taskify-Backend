from sqlalchemy.orm import Mapped, mapped_column
from enum import Enum as PyEnum
from datetime import datetime, timezone
from sqlalchemy import (
    String,
    Boolean,
    DateTime,
    Enum as SqlEnum
)
from app.db.base import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid


class PasswordResetCode(Base):
    __tablename__ = "password_reset_codes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    code: Mapped[str] = mapped_column(String(6), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False)