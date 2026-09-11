"""Wires the LangGraph agent to FastAPI, DB checkpointer, and SSE."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any
from uuid import UUID, uuid4

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.types import Command

from app.agent.graph import build_graph
from app.core.config import get_settings


class AgentService:
    """One instance per application (kept in app.state)."""

    def __init__(self) -> None:
        self._graph = None
        self._checkpointer_ctx = None
        self._checkpointer: AsyncPostgresSaver | None = None

    async def start(self) -> None:
        settings = get_settings()
        dsn = settings.database_url.replace("+asyncpg", "")
        self._checkpointer_ctx = AsyncPostgresSaver.from_conn_string(dsn)
        self._checkpointer = await self._checkpointer_ctx.__aenter__()
        await self._checkpointer.setup()
        self._graph = build_graph(checkpointer=self._checkpointer)

    async def stop(self) -> None:
        if self._checkpointer_ctx is not None:
            await self._checkpointer_ctx.__aexit__(None, None, None)

    def _thread_config(self, user_id: UUID, thread_id: str) -> dict[str, Any]:
        return {
            "configurable": {
                "thread_id": thread_id,
                "user_id": str(user_id),
            }
        }

    async def start_thread(self, user_id: UUID, thread_id: str | None = None) -> str:
        return thread_id or str(uuid4())

    async def run(
        self,
        *,
        user_id: UUID,
        message: str,
        thread_id: str,
        timezone: str = "UTC",
        language: str = "fr",
    ) -> AsyncIterator[dict[str, Any]]:
        assert self._graph is not None
        config = self._thread_config(user_id, thread_id)
        inputs = {
            "raw_user_input": message,
            "messages": [],
            "user_id": str(user_id),
            "timezone": timezone,
            "language": language,
        }

        async for event in self._graph.astream_events(
            inputs, config=config, version="v2"
        ):
            kind = event["event"]
            if kind == "on_chain_end" and event.get("name") == "LangGraph":
                output = event["data"].get("output", {})
                yield {
                    "type": "final",
                    "status": output.get("status"),
                    "intent": output.get("intent"),
                    "response": output.get("final_response"),
                    "tool_results": output.get("tool_results", []),
                    "planned_actions": output.get("planned_actions", []),
                }

    async def resume(
        self,
        *,
        user_id: UUID,
        thread_id: str,
        approved: bool,
    ) -> AsyncIterator[dict[str, Any]]:
        assert self._graph is not None
        config = self._thread_config(user_id, thread_id)
        async for event in self._graph.astream_events(
            Command(resume=approved), config=config, version="v2"
        ):
            if event["event"] == "on_chain_end" and event.get("name") == "LangGraph":
                output = event["data"].get("output", {})
                yield {
                    "type": "final",
                    "status": output.get("status"),
                    "response": output.get("final_response"),
                    "tool_results": output.get("tool_results", []),
                }


_agent_service: AgentService | None = None


def get_agent_service() -> AgentService:
    global _agent_service
    if _agent_service is None:
        _agent_service = AgentService()
    return _agent_service
