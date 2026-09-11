from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Query, status

from app.api.deps import CurrentUser, DbSession
from app.schemas.event import EventCreate, EventPublic, EventUpdate
from app.services.calendar_service import CalendarService

router = APIRouter()


@router.get("", response_model=list[EventPublic])
async def list_events(
    user: CurrentUser,
    db: DbSession,
    start: datetime = Query(default_factory=lambda: datetime.now(UTC)),
    end: datetime = Query(
        default_factory=lambda: datetime.now(UTC) + timedelta(days=7)
    ),
    sync: bool = True,
) -> list[EventPublic]:
    events = await CalendarService(db).list_events(user.id, start, end, sync=sync)
    return [EventPublic.model_validate(e) for e in events]


@router.post("", response_model=EventPublic, status_code=status.HTTP_201_CREATED)
async def create_event(
    payload: EventCreate, user: CurrentUser, db: DbSession
) -> EventPublic:
    event = await CalendarService(db).create_event(
        user.id,
        summary=payload.summary,
        start_at=payload.start_at,
        end_at=payload.end_at,
        description=payload.description,
        location=payload.location,
        all_day=payload.all_day,
        calendar_id=payload.calendar_id,
    )
    return EventPublic.model_validate(event)


@router.patch("/{event_id}", response_model=EventPublic)
async def update_event(
    event_id: str, payload: EventUpdate, user: CurrentUser, db: DbSession
) -> EventPublic:
    event = await CalendarService(db).update_event(
        user.id, event_id, **payload.model_dump(exclude_unset=True)
    )
    return EventPublic.model_validate(event)


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(event_id: str, user: CurrentUser, db: DbSession) -> None:
    await CalendarService(db).delete_event(user.id, event_id)
