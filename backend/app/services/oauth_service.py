from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, decode_token
from app.integrations.google_calendar import (
    build_auth_url,
    exchange_code_for_tokens,
)
from app.repositories.oauth_repository import OAuthRepository


class OAuthService:
    STATE_PURPOSE = "oauth_state"

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = OAuthRepository(db)

    def build_state(self, user_id: UUID) -> str:
        return create_access_token(str(user_id))

    def parse_state(self, state: str) -> UUID:
        try:
            payload = decode_token(state, expected_type="access")
            return UUID(payload["sub"])
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OAuth state",
            ) from e

    def build_consent_url(self, user_id: UUID) -> str:
        return build_auth_url(state=self.build_state(user_id))

    async def handle_callback(self, code: str, state: str) -> UUID:
        user_id = self.parse_state(state)
        tokens = await exchange_code_for_tokens(code)

        access_token = tokens.get("access_token")
        refresh_token = tokens.get("refresh_token")
        expires_in = tokens.get("expires_in")
        scope = tokens.get("scope", "")

        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Google did not return an access token",
            )

        expires_at = (
            datetime.now(UTC) + timedelta(seconds=int(expires_in))
            if expires_in
            else None
        )

        await self.repo.upsert(
            user_id=user_id,
            provider="google",
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            scopes=scope,
        )
        return user_id
