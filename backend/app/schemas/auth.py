from __future__ import annotations

from pydantic import BaseModel


class GoogleAuthURL(BaseModel):
    auth_url: str


class MessageResponse(BaseModel):
    message: str