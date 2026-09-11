from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event_cache import EventCache


class EventRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_in_range(
        self, user_id: UUID, start: datetime, end: datetime
    ) -> list[EventCache]:
        stmt = (
            select(EventCache)
            .where(
                EventCache.user_id == user_id,
                EventCache.end_at > start,
                EventCache.start_at < end,
            )
            .order_by(EventCache.start_at)
        )
        return list((await self.db.execute(stmt)).scalars().all())

    async def get_by_google_id(
        self, user_id: UUID, google_event_id: str
    ) -> EventCache | None:
        stmt = select(EventCache).where(
            EventCache.user_id == user_id,
            EventCache.google_event_id == google_event_id,
        )
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def upsert_from_google(
        self, user_id: UUID, payload: dict[str, Any]
    ) -> EventCache:
        google_id = payload["id"]
        existing = await self.get_by_google_id(user_id, google_id)

        start_raw = payload.get("start", {})
        end_raw = payload.get("end", {})
        all_day = "date" in start_raw

        def _parse(node: dict[str, Any]) -> datetime:
            from datetime import UTC

            if "dateTime" in node:
                return datetime.fromisoformat(node["dateTime"])
            return datetime.fromisoformat(node["date"]).replace(tzinfo=UTC)

        fields = {
            "summary": payload.get("summary", ""),
            "description": payload.get("description"),
            "location": payload.get("location"),
            "start_at": _parse(start_raw),
            "end_at": _parse(end_raw),
            "all_day": all_day,
            "timezone": start_raw.get("timeZone"),
            "etag": payload.get("etag"),
            "raw_json": payload,
        }

        if existing is None:
            existing = EventCache(
                user_id=user_id,
                google_event_id=google_id,
                **fields,
            )
            self.db.add(existing)
        else:
            for k, v in fields.items():
                setattr(existing, k, v)

        await self.db.flush()
        return existing

    async def delete_by_google_id(self, user_id: UUID, google_event_id: str) -> None:
        stmt = delete(EventCache).where(
            EventCache.user_id == user_id,
            EventCache.google_event_id == google_event_id,
        )
        await self.db.execute(stmt)
