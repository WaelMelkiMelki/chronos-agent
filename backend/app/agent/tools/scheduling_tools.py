from __future__ import annotations


from datetime import datetime


from langchain_core.tools import tool
from pydantic import BaseModel, Field




class FindFreeSlotsInput(BaseModel):
    range_start: datetime
    range_end: datetime
    duration_minutes: int = Field(..., ge=5, le=480)
    calendar_id: str = "primary"




@tool("find_free_slots", args_schema=FindFreeSlotsInput)
async def find_free_slots(**kwargs) -> list[dict]:  # type: ignore[no-untyped-def]
    """Find free slots of the requested duration respecting user rules."""
    raise NotImplementedError("Wired to SchedulingRulesEngine in Phase 3")
