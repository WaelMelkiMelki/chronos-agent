from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.google_calendar import GoogleCalendarClient
from app.models.event_cache import EventCache
from app.repositories.event_repository import EventRepository
from app.repositories.oauth_repository import OAuthRepository


class CalendarService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.events = EventRepository(db)
        self.oauth = OAuthRepository(db)

    async def _client(self, user_id: UUID) -> GoogleCalendarClient:
        token = await self.oauth.get(user_id, "google")
        if token is None:
            raise HTTPException(
                status_code=status.HTTP_412_PRECONDITION_FAILED,
                detail="Google Calendar not connected. Please connect first.",
            )
        return GoogleCalendarClient(
            access_token=OAuthRepository.decrypt_access(token),
            refresh_token=OAuthRepository.decrypt_refresh(token),
            expires_at=token.expires_at,
            scopes=token.scopes.split() if token.scopes else None,
        )

    async def sync_range(
        self, user_id: UUID, start: datetime, end: datetime
    ) -> list[EventCache]:
        client = await self._client(user_id)
        items = await client.list_events(time_min=start, time_max=end)
        for item in items:
            await self.events.upsert_from_google(user_id, item)
        return await self.events.list_in_range(user_id, start, end)

    async def list_events(
        self, user_id: UUID, start: datetime, end: datetime, *, sync: bool = True
    ) -> list[EventCache]:
        if sync:
            return await self.sync_range(user_id, start, end)
        return await self.events.list_in_range(user_id, start, end)

    async def create_event(
        self,
        user_id: UUID,
        *,
        summary: str,
        start_at: datetime,
        end_at: datetime,
        description: str | None = None,
        location: str | None = None,
        all_day: bool = False,
        calendar_id: str = "primary",
    ) -> EventCache:
        client = await self._client(user_id)
        body = self._build_body(
            summary=summary, start_at=start_at, end_at=end_at,
            description=description, location=location, all_day=all_day,
        )
        created = await client.create_event(body, calendar_id=calendar_id)
        return await self.events.upsert_from_google(user_id, created)

    async def update_event(
        self,
        user_id: UUID,
        google_event_id: str,
        **fields: Any,
    ) -> EventCache:
        client = await self._client(user_id)
        body: dict[str, Any] = {}
        if "summary" in fields and fields["summary"] is not None:
            body["summary"] = fields["summary"]
        if "description" in fields:
            body["description"] = fields["description"]
        if "location" in fields:
            body["location"] = fields["location"]
        if fields.get("start_at") or fields.get("end_at"):
            existing = await self.events.get_by_google_id(user_id, google_event_id)
            if existing is None:
                raise HTTPException(404, "Event not found")
            start = fields.get("start_at") or existing.start_at
            end = fields.get("end_at") or existing.end_at
            body["start"] = {"dateTime": start.isoformat(), "timeZone": "UTC"}
            body["end"] = {"dateTime": end.isoformat(), "timeZone": "UTC"}
        updated = await client.update_event(google_event_id, body)
        return await self.events.upsert_from_google(user_id, updated)

    async def delete_event(self, user_id: UUID, google_event_id: str) -> None:
        client = await self._client(user_id)
        await client.delete_event(google_event_id)
        await self.events.delete_by_google_id(user_id, google_event_id)

    @staticmethod
    def _build_body(
        *,
        summary: str,
        start_at: datetime,
        end_at: datetime,
        description: str | None,
        location: str | None,
        all_day: bool,
    ) -> dict[str, Any]:
        if all_day:
            body_start = {"date": start_at.date().isoformat()}
            body_end = {"date": (end_at.date() + timedelta(days=1)).isoformat()}
        else:
            body_start = {"dateTime": start_at.astimezone(UTC).isoformat(), "timeZone": "UTC"}
            body_end = {"dateTime": end_at.astimezone(UTC).isoformat(), "timeZone": "UTC"}

        body: dict[str, Any] = {"summary": summary, "start": body_start, "end": body_end}
        if description:
            body["description"] = description
        if location:
            body["location"] = location
        return body
