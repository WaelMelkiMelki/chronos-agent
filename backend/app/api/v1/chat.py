"""Chat endpoint: streams LangGraph agent events via SSE."""


from __future__ import annotations


import json
from collections.abc import AsyncIterator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.services.agent_service import AgentService


router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    thread_id: str | None = None


@router.post("")
async def chat(req: ChatRequest) -> StreamingResponse:
    """Run the LangGraph agent and stream events via SSE."""
    async def event_generator() -> AsyncIterator[str]:
        service = AgentService()
        async for event in service.run(req.message, thread_id=req.thread_id):
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )
