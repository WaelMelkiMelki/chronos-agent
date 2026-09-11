from __future__ import annotations


from typing import TYPE_CHECKING, Any
from uuid import UUID


from datetime import datetime


from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


from app.db.base import Base, TimestampMixin, UUIDMixin


if TYPE_CHECKING:
    from app.models.user import User




class AuditLog(UUIDMixin, TimestampMixin, Base):
    """Immutable record of every mutating action, enabling undo/rollback."""


    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_user_created", "user_id", "created_at"),
        Index("ix_audit_entity", "entity_type", "entity_id"),
    )


    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    action_type: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_id: Mapped[str | None] = mapped_column(String(255))


    old_value: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    new_value: Mapped[dict[str, Any] | None] = mapped_column(JSONB)


    executed_by: Mapped[str] = mapped_column(String(32), default="agent", nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="success", nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text)
    undone_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


    user: Mapped[User] = relationship(back_populates="audit_logs")
