from __future__ import annotations


from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID


from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


from app.db.base import Base, TimestampMixin, UUIDMixin


if TYPE_CHECKING:
    from app.models.user import User




class OAuthToken(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "oauth_tokens"
    __table_args__ = (UniqueConstraint("user_id", "provider", name="uq_user_provider"),)


    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    provider: Mapped[str] = mapped_column(String(32), nullable=False)  # "google"
    access_token_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    refresh_token_encrypted: Mapped[str | None] = mapped_column(Text)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    scopes: Mapped[str] = mapped_column(Text, default="", nullable=False)


    user: Mapped[User] = relationship(back_populates="oauth_tokens")
