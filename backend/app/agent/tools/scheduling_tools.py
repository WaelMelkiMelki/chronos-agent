from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from app.db.session import get_session_factory
from app.services.calendar_service import CalendarService


class FindFreeSlotsInput(BaseModel):
    range_start: datetime
    range_end: datetime
    duration_minutes: int = Field(..., ge=5, le=480)
    office_start_hour: int = 9
    office_end_hour: int = 18
    buffer_minutes: int = 10


@tool("find_free_slots", args_schema=FindFreeSlotsInput)
async def find_free_slots(
    range_start: datetime, range_end: datetime,
    duration_minutes: int,
    office_start_hour: int = 9,
    office_end_hour: int = 18,
    buffer_minutes: int = 10,
    config: RunnableConfig | None = None,
) -> list[dict[str, Any]]:
    cfg = config or {}
    user_id = UUID(str(cfg.get("configurable", {}).get("user_id")))
    factory = get_session_factory()
    async with factory() as db:
        events = await CalendarService(db).list_events(user_id, range_start, range_end)
    busy = sorted([(e.start_at, e.end_at) for e in events if not e.all_day], key=lambda x: x[0])
    duration = timedelta(minutes=duration_minutes)
    buffer = timedelta(minutes=buffer_minutes)
    slots: list[dict[str, Any]] = []
    day = range_start.date()
    end_date = range_end.date()
    while day <= end_date:
        if day.weekday() >= 5:
            day += timedelta(days=1)
            continue
        cursor = datetime.combine(day, datetime.min.time()).replace(hour=office_start_hour, tzinfo=UTC)
        day_end = cursor.replace(hour=office_end_hour)
        day_busy = [(max(s, cursor), min(e, day_end)) for s, e in busy if e > cursor and s < day_end]
        day_busy.sort()
        for bs, be in day_busy:
            if (bs - cursor) >= duration:
                slots.append({"start": cursor.isoformat(), "end": (cursor + duration).isoformat()})
            cursor = max(cursor, be + buffer)
        if (day_end - cursor) >= duration:
            slots.append({"start": cursor.isoformat(), "end": (cursor + duration).isoformat()})
        day += timedelta(days=1)
    return slots
