from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class EventBase(BaseModel):
    summary: str = Field(..., max_length=500)
    description: str | None = None
    location: str | None = None
    start_at: datetime
    end_at: datetime
    all_day: bool = False
    timezone: str | None = None
    calendar_id: str = "primary"


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    summary: str | None = None
    description: str | None = None
    location: str | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    all_day: bool | None = None


class EventPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    google_event_id: str
    summary: str
    description: str | None
    location: str | None
    start_at: datetime
    end_at: datetime
    all_day: bool
    calendar_id: str


class FreeSlot(BaseModel):
    start_at: datetime
    end_at: datetime
    duration_minutes: int