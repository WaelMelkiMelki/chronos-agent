from __future__ import annotations


from datetime import time
from typing import TYPE_CHECKING
from uuid import UUID


from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, Time
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


from app.db.base import Base, TimestampMixin, UUIDMixin


if TYPE_CHECKING:
    from app.models.user import User




class UserSettings(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "user_settings"


    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )


    # Localization
    language: Mapped[str] = mapped_column(String(8), default="fr", nullable=False)
    timezone: Mapped[str] = mapped_column(String(64), default="Europe/Paris", nullable=False)


    # LLM preferences (per-user override of env defaults)
    llm_provider: Mapped[str | None] = mapped_column(String(32))
    llm_model: Mapped[str | None] = mapped_column(String(128))
    llm_api_key_encrypted: Mapped[str | None] = mapped_column(Text)


    # Scheduling rules
    office_hours_start: Mapped[time] = mapped_column(Time, default=time(9, 0), nullable=False)
    office_hours_end: Mapped[time] = mapped_column(Time, default=time(18, 0), nullable=False)
    lunch_start: Mapped[time] = mapped_column(Time, default=time(12, 0), nullable=False)
    lunch_end: Mapped[time] = mapped_column(Time, default=time(13, 0), nullable=False)
    buffer_minutes: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    min_meeting_minutes: Mapped[int] = mapped_column(Integer, default=15, nullable=False)
    max_meeting_minutes: Mapped[int] = mapped_column(Integer, default=240, nullable=False)
    allow_overlap: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    working_days: Mapped[str] = mapped_column(
        String(32), default="1,2,3,4,5", nullable=False
    )  # ISO weekday numbers 1=Mon … 7=Sun


    user: Mapped[User] = relationship(back_populates="settings")
