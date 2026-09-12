"""Calendar tools bound to the LangGraph agent (function-calling)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from app.db.session import get_session_factory
from app.services.calendar_service import CalendarService


def _user_id_from_config(config: RunnableConfig) -> str:
    cfg = config.get("configurable", {})
    user_id = cfg.get("user_id")
    if not user_id:
        raise ValueError("user_id missing from runnable config")
    return str(user_id)


class ListEventsInput(BaseModel):
    start: datetime = Field(..., description="Range start (ISO 8601)")
    end: datetime = Field(..., description="Range end (ISO 8601)")
    calendar_id: str = "primary"


class CreateEventInput(BaseModel):
    summary: str
    start: datetime
    end: datetime
    description: str | None = None
    location: str | None = None
    all_day: bool = False
    calendar_id: str = "primary"


class UpdateEventInput(BaseModel):
    google_event_id: str
    summary: str | None = None
    start: datetime | None = None
    end: datetime | None = None
    description: str | None = None
    location: str | None = None


class DeleteEventInput(BaseModel):
    google_event_id: str


@tool("list_events", args_schema=ListEventsInput)
async def list_events(
    start: datetime,
    end: datetime,
    calendar_id: str = "primary",
    config: RunnableConfig | None = None,
) -> list[dict[str, Any]]:
    """List calendar events between two datetimes."""
    user_id = _user_id_from_config(config or {})
    factory = get_session_factory()
    async with factory() as db:
        events = await CalendarService(db).list_events(user_id, start, end)
        return [
            {
                "id": e.google_event_id,
                "summary": e.summary,
                "start": e.start_at.isoformat(),
                "end": e.end_at.isoformat(),
                "all_day": e.all_day,
            }
            for e in events
        ]


@tool("create_event", args_schema=CreateEventInput)
async def create_event(
    summary: str,
    start: datetime,
    end: datetime,
    description: str | None = None,
    location: str | None = None,
    all_day: bool = False,
    calendar_id: str = "primary",
    config: RunnableConfig | None = None,
) -> dict[str, Any]:
    """Create a new calendar event."""
    from uuid import UUID

    user_id = UUID(_user_id_from_config(config or {}))
    factory = get_session_factory()
    async with factory() as db:
        event = await CalendarService(db).create_event(
            user_id,
            summary=summary,
            start_at=start,
            end_at=end,
            description=description,
            location=location,
            all_day=all_day,
            calendar_id=calendar_id,
        )
        await db.commit()
        return {"id": event.google_event_id, "summary": event.summary}


@tool("update_event", args_schema=UpdateEventInput)
async def update_event(
    google_event_id: str,
    summary: str | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
    description: str | None = None,
    location: str | None = None,
    config: RunnableConfig | None = None,
) -> dict[str, Any]:
    """Update an existing calendar event."""
    from uuid import UUID

    user_id = UUID(_user_id_from_config(config or {}))
    factory = get_session_factory()
    async with factory() as db:
        event = await CalendarService(db).update_event(
            user_id,
            google_event_id,
            summary=summary,
            start_at=start,
            end_at=end,
            description=description,
            location=location,
        )
        await db.commit()
        return {"id": event.google_event_id, "summary": event.summary}


@tool("delete_event", args_schema=DeleteEventInput)
async def delete_event(
    google_event_id: str, config: RunnableConfig | None = None
) -> dict[str, Any]:
    """Delete an existing calendar event."""
    from uuid import UUID

    user_id = UUID(_user_id_from_config(config or {}))
    factory = get_session_factory()
    async with factory() as db:
        await CalendarService(db).delete_event(user_id, google_event_id)
        await db.commit()
        return {"deleted": google_event_id}


__all__ = [
    "list_events",
    "create_event",
    "update_event",
    "delete_event",
]
