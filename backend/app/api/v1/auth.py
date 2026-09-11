from fastapi import APIRouter


router = APIRouter()




@router.get("/google/login")
async def google_login() -> dict[str, str]:
    """TODO Phase 2: return the Google OAuth consent URL."""
    return {"status": "not_implemented"}




@router.get("/google/callback")
async def google_callback(code: str | None = None) -> dict[str, str]:
    """TODO Phase 2: exchange code, encrypt tokens, store them."""
    return {"status": "not_implemented", "code": code or ""}
