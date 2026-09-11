"""Calendar tools exposed to the LangGraph agent (function-calling).


V1 uses plain Python functions wrapped with @tool. In V2, the same
operations are re-exposed through MCP servers.
"""


from __future__ import annotations


from datetime import datetime


from langchain_core.tools import tool
from pydantic import BaseModel, Field




class ListEventsInput(BaseModel):
    start: datetime = Field(..., description="Range start (inclusive, ISO 8601)")
    end: datetime = Field(..., description="Range end (exclusive, ISO 8601)")
    calendar_id: str = Field("primary", description="Google Calendar ID")




class CreateEventInput(BaseModel):
    summary: str
    start: datetime
    end: datetime
    description: str | None = None
    location: str | None = None
    all_day: bool = False
    calendar_id: str = "primary"




class UpdateEventInput(BaseModel):
    event_id: str
    summary: str | None = None
    start: datetime | None = None
    end: datetime | None = None
    description: str | None = None
    location: str | None = None




class DeleteEventInput(BaseModel):
    event_id: str




@tool("list_events", args_schema=ListEventsInput)
async def list_events(
    start: datetime, end: datetime, calendar_id: str = "primary"
) -> list[dict]:
    """List events between two datetimes."""
    raise NotImplementedError("Wired to CalendarService in Phase 2")




@tool("create_event", args_schema=CreateEventInput)
async def create_event(**kwargs) -> dict:  # type: ignore[no-untyped-def]
    """Create a calendar event."""
    raise NotImplementedError("Wired to CalendarService in Phase 2")




@tool("update_event", args_schema=UpdateEventInput)
async def update_event(**kwargs) -> dict:  # type: ignore[no-untyped-def]
    """Update an existing calendar event."""
    raise NotImplementedError("Wired to CalendarService in Phase 2")




@tool("delete_event", args_schema=DeleteEventInput)
async def delete_event(event_id: str) -> dict:
    """Delete a calendar event."""
    raise NotImplementedError("Wired to CalendarService in Phase 2")
