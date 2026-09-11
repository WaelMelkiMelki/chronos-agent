from __future__ import annotations


from typing import TYPE_CHECKING


from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


from app.db.base import Base, TimestampMixin, UUIDMixin


if TYPE_CHECKING:
    from app.models.audit_log import AuditLog
    from app.models.event_cache import EventCache
    from app.models.oauth_token import OAuthToken
    from app.models.user_settings import UserSettings




class User(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "users"


    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


    oauth_tokens: Mapped[list[OAuthToken]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    settings: Mapped[UserSettings | None] = relationship(
        back_populates="user", cascade="all, delete-orphan", uselist=False
    )
    events: Mapped[list[EventCache]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    audit_logs: Mapped[list[AuditLog]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
