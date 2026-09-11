from __future__ import annotations

from fastapi import APIRouter, status
from fastapi.responses import RedirectResponse

from app.api.deps import CurrentUser, DbSession
from app.core.config import get_settings
from app.schemas.auth import GoogleAuthURL, MessageResponse
from app.schemas.user import (
    RefreshRequest,
    TokenPair,
    UserCreate,
    UserLogin,
    UserPublic,
)
from app.services.auth_service import AuthService
from app.services.oauth_service import OAuthService

router = APIRouter()


@router.post("/register", response_model=TokenPair, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, db: DbSession) -> TokenPair:
    _user, tokens = await AuthService(db).register(payload)
    return tokens


@router.post("/login", response_model=TokenPair)
async def login(payload: UserLogin, db: DbSession) -> TokenPair:
    _user, tokens = await AuthService(db).login(payload.email, payload.password)
    return tokens


@router.post("/refresh", response_model=TokenPair)
async def refresh(payload: RefreshRequest, db: DbSession) -> TokenPair:
    return await AuthService(db).refresh(payload.refresh_token)


@router.get("/me", response_model=UserPublic)
async def me(user: CurrentUser) -> UserPublic:
    return UserPublic.model_validate(user)


@router.post("/logout", response_model=MessageResponse)
async def logout(_user: CurrentUser) -> MessageResponse:
    return MessageResponse(message="Logged out")


@router.get("/google/login", response_model=GoogleAuthURL)
async def google_login(user: CurrentUser, db: DbSession) -> GoogleAuthURL:
    url = OAuthService(db).build_consent_url(user.id)
    return GoogleAuthURL(auth_url=url)


@router.get("/google/callback")
async def google_callback(
    db: DbSession,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
) -> RedirectResponse:
    settings = get_settings()
    redirect = f"{settings.frontend_url}/auth/callback"

    if error or not code or not state:
        return RedirectResponse(f"{redirect}?status=error")

    try:
        await OAuthService(db).handle_callback(code, state)
    except HTTPException:
        return RedirectResponse(f"{redirect}?status=error")

    return RedirectResponse(f"{redirect}?status=success")
