"""Thin async-friendly wrapper around the sync Google Calendar client."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlencode

import httpx
from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from app.core.config import get_settings

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


def build_auth_url(state: str) -> str:
    settings = get_settings()
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": settings.google_scopes,
        "access_type": "offline",
        "prompt": "consent",
        "include_granted_scopes": "true",
        "state": state,
    }
    return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"


async def exchange_code_for_tokens(code: str) -> dict[str, Any]:
    settings = get_settings()
    data = {
        "code": code,
        "client_id": settings.google_client_id,
        "client_secret": settings.google_client_secret,
        "redirect_uri": settings.google_redirect_uri,
        "grant_type": "authorization_code",
    }
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(GOOGLE_TOKEN_URL, data=data)
        resp.raise_for_status()
        return resp.json()


async def refresh_access_token(refresh_token: str) -> dict[str, Any]:
    settings = get_settings()
    data = {
        "client_id": settings.google_client_id,
        "client_secret": settings.google_client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(GOOGLE_TOKEN_URL, data=data)
        resp.raise_for_status()
        return resp.json()


class GoogleCalendarClient:
    def __init__(
        self,
        *,
        access_token: str,
        refresh_token: str | None,
        expires_at: datetime | None,
        scopes: list[str] | None = None,
    ) -> None:
        self._creds = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri=GOOGLE_TOKEN_URL,
            client_id=get_settings().google_client_id,
            client_secret=get_settings().google_client_secret,
            scopes=scopes or [get_settings().google_scopes],
            expiry=expires_at.replace(tzinfo=None) if expires_at else None,
        )

    def _service(self):
        if not self._creds.valid:
            self._creds.refresh(GoogleRequest())
        return build("calendar", "v3", credentials=self._creds, cache_discovery=False)

    async def _run(self, fn, *args, **kwargs):
        return await asyncio.to_thread(fn, *args, **kwargs)

    async def list_events(
        self, *, time_min: datetime, time_max: datetime, calendar_id: str = "primary"
    ) -> list[dict[str, Any]]:
        def _call() -> list[dict[str, Any]]:
            svc = self._service()
            result = (
                svc.events()
                .list(
                    calendarId=calendar_id,
                    timeMin=time_min.astimezone(UTC).isoformat().replace("+00:00", "Z"),
                    timeMax=time_max.astimezone(UTC).isoformat().replace("+00:00", "Z"),
                    singleEvents=True,
                    orderBy="startTime",
                    maxResults=250,
                )
                .execute()
            )
            return result.get("items", [])

        return await self._run(_call)

    async def create_event(self, body: dict[str, Any], calendar_id: str = "primary") -> dict:
        def _call() -> dict[str, Any]:
            svc = self._service()
            return svc.events().insert(calendarId=calendar_id, body=body).execute()
        return await self._run(_call)

    async def update_event(
        self, event_id: str, body: dict[str, Any], calendar_id: str = "primary"
    ) -> dict:
        def _call() -> dict[str, Any]:
            svc = self._service()
            return (
                svc.events()
                .patch(calendarId=calendar_id, eventId=event_id, body=body)
                .execute()
            )
        return await self._run(_call)

    async def delete_event(self, event_id: str, calendar_id: str = "primary") -> None:
        def _call() -> None:
            svc = self._service()
            svc.events().delete(calendarId=calendar_id, eventId=event_id).execute()
        await self._run(_call)
