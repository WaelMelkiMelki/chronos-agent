from __future__ import annotations


from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID


from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


from app.db.base import Base, TimestampMixin, UUIDMixin


if TYPE_CHECKING:
    from app.models.user import User




class EventCache(UUIDMixin, TimestampMixin, Base):
    """Local mirror of Google Calendar events (fast reads, offline search)."""


    __tablename__ = "events_cache"
    __table_args__ = (
        Index("ix_events_user_start_end", "user_id", "start_at", "end_at"),
    )


    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    calendar_id: Mapped[str] = mapped_column(String(255), default="primary", nullable=False)
    google_event_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)


    summary: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    location: Mapped[str | None] = mapped_column(String(500))


    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    all_day: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    timezone: Mapped[str | None] = mapped_column(String(64))


    etag: Mapped[str | None] = mapped_column(String(128))
    raw_json: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)


    user: Mapped[User] = relationship(back_populates="events")
