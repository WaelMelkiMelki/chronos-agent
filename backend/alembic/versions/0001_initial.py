"""initial schema


Revision ID: 0001_initial
Revises:
Create Date: 2026-09-10
"""
from __future__ import annotations


from collections.abc import Sequence


import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None




def upgrade() -> None:
    # ─── users ─────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(320), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255)),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"])


    # ─── user_settings ─────────────────────────
    op.create_table(
        "user_settings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("language", sa.String(8), nullable=False, server_default="fr"),
        sa.Column("timezone", sa.String(64), nullable=False, server_default="Europe/Paris"),
        sa.Column("llm_provider", sa.String(32)),
        sa.Column("llm_model", sa.String(128)),
        sa.Column("llm_api_key_encrypted", sa.Text()),
        sa.Column("office_hours_start", sa.Time(), nullable=False, server_default="09:00:00"),
        sa.Column("office_hours_end", sa.Time(), nullable=False, server_default="18:00:00"),
        sa.Column("lunch_start", sa.Time(), nullable=False, server_default="12:00:00"),
        sa.Column("lunch_end", sa.Time(), nullable=False, server_default="13:00:00"),
        sa.Column("buffer_minutes", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("min_meeting_minutes", sa.Integer(), nullable=False, server_default="15"),
        sa.Column("max_meeting_minutes", sa.Integer(), nullable=False, server_default="240"),
        sa.Column("allow_overlap", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("working_days", sa.String(32), nullable=False, server_default="1,2,3,4,5"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_user_settings_user_id", "user_settings", ["user_id"])


    # ─── oauth_tokens ──────────────────────────
    op.create_table(
        "oauth_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("provider", sa.String(32), nullable=False),
        sa.Column("access_token_encrypted", sa.Text(), nullable=False),
        sa.Column("refresh_token_encrypted", sa.Text()),
        sa.Column("expires_at", sa.DateTime(timezone=True)),
        sa.Column("scopes", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", "provider", name="uq_user_provider"),
    )
    op.create_index("ix_oauth_tokens_user_id", "oauth_tokens", ["user_id"])


    # ─── events_cache ──────────────────────────
    op.create_table(
        "events_cache",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("calendar_id", sa.String(255), nullable=False, server_default="primary"),
        sa.Column("google_event_id", sa.String(255), nullable=False),
        sa.Column("summary", sa.String(500), nullable=False, server_default=""),
        sa.Column("description", sa.Text()),
        sa.Column("location", sa.String(500)),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("all_day", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("timezone", sa.String(64)),
        sa.Column("etag", sa.String(128)),
        sa.Column("raw_json", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_events_cache_user_id", "events_cache", ["user_id"])
    op.create_index("ix_events_cache_google_event_id", "events_cache", ["google_event_id"])
    op.create_index("ix_events_user_start_end", "events_cache", ["user_id", "start_at", "end_at"])


    # ─── audit_logs ────────────────────────────
    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("action_type", sa.String(64), nullable=False),
        sa.Column("entity_type", sa.String(64), nullable=False),
        sa.Column("entity_id", sa.String(255)),
        sa.Column("old_value", postgresql.JSONB()),
        sa.Column("new_value", postgresql.JSONB()),
        sa.Column("executed_by", sa.String(32), nullable=False, server_default="agent"),
        sa.Column("status", sa.String(32), nullable=False, server_default="success"),
        sa.Column("error_message", sa.Text()),
        sa.Column("undone_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"])
    op.create_index("ix_audit_user_created", "audit_logs", ["user_id", "created_at"])
    op.create_index("ix_audit_entity", "audit_logs", ["entity_type", "entity_id"])




def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("events_cache")
    op.drop_table("oauth_tokens")
    op.drop_table("user_settings")
    op.drop_table("users")
