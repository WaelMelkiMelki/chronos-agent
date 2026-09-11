from fastapi import APIRouter


router = APIRouter()




@router.get("")
async def list_audit() -> list[dict]:
    """TODO Phase 4: paginated audit log."""
    return []
