from fastapi import APIRouter


router = APIRouter()




@router.get("")
async def list_events() -> list[dict]:
    """TODO Phase 3: return events from events_cache."""
    return []
