from __future__ import annotations

import json
from collections.abc import AsyncIterator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.api.deps import CurrentUser
from app.services.agent_service import get_agent_service

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    thread_id: str | None = None


class ConfirmRequest(BaseModel):
    thread_id: str
    approved: bool


def _sse(payload: dict) -> str:
    return f"data: {json.dumps(payload, default=str)}\n\n"


@router.post("")
async def chat(req: ChatRequest, user: CurrentUser) -> StreamingResponse:
    agent = get_agent_service()
    thread_id = await agent.start_thread(user.id, req.thread_id)

    async def _gen() -> AsyncIterator[str]:
        yield _sse({"type": "thread", "thread_id": thread_id})
        async for event in agent.run(
            user_id=user.id, message=req.message, thread_id=thread_id
        ):
            yield _sse(event)

    return StreamingResponse(
        _gen(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@router.post("/confirm")
async def confirm(req: ConfirmRequest, user: CurrentUser) -> StreamingResponse:
    agent = get_agent_service()

    async def _gen() -> AsyncIterator[str]:
        async for event in agent.resume(
            user_id=user.id, thread_id=req.thread_id, approved=req.approved
        ):
            yield _sse(event)

    return StreamingResponse(_gen(), media_type="text/event-stream")
