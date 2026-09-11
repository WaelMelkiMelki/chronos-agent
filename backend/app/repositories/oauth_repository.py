from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decrypt_secret, encrypt_secret
from app.models.oauth_token import OAuthToken


class OAuthRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get(self, user_id: UUID, provider: str = "google") -> OAuthToken | None:
        stmt = select(OAuthToken).where(
            OAuthToken.user_id == user_id, OAuthToken.provider == provider
        )
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def upsert(
        self,
        *,
        user_id: UUID,
        provider: str,
        access_token: str,
        refresh_token: str | None,
        expires_at: datetime | None,
        scopes: str,
    ) -> OAuthToken:
        existing = await self.get(user_id, provider)
        if existing is None:
            existing = OAuthToken(user_id=user_id, provider=provider)
            self.db.add(existing)

        existing.access_token_encrypted = encrypt_secret(access_token)
        if refresh_token:
            existing.refresh_token_encrypted = encrypt_secret(refresh_token)
        existing.expires_at = expires_at
        existing.scopes = scopes
        await self.db.flush()
        return existing

    @staticmethod
    def decrypt_access(token: OAuthToken) -> str:
        return decrypt_secret(token.access_token_encrypted)

    @staticmethod
    def decrypt_refresh(token: OAuthToken) -> str | None:
        if not token.refresh_token_encrypted:
            return None
        return decrypt_secret(token.refresh_token_encrypted)
