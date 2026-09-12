"""Wires the LangGraph agent to FastAPI, DB checkpointer, and SSE."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any
from uuid import UUID, uuid4

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.types import Command

from app.agent.graph import build_graph
from app.core.config import get_settings


_TERMINAL_STATUSES = {"done", "awaiting_confirmation", "awaiting_clarification", "error"}


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

    def _final_payload(self, values: dict[str, Any]) -> dict[str, Any]:
        """Build the SSE payload from a LangGraph state dict."""
        return {
            "type": "final",
            "status": values.get("status"),
            "intent": values.get("intent"),
            "response": values.get("final_response"),
            "clarification_question": values.get("clarification_question"),
            "tool_results": values.get("tool_results", []),
            "planned_actions": values.get("planned_actions", []),
        }

    async def run(
        self,
        *,
        user_id: UUID,
        message: str,
        thread_id: str,
        timezone: str = "UTC",
        language: str = "fr",
    ) -> AsyncIterator[dict[str, Any]]:
        """Run the graph and stream only the final terminal state as SSE."""
        assert self._graph is not None

        config = self._thread_config(user_id, thread_id)
        inputs = {
            "raw_user_input": message,
            "messages": [],
            "user_id": str(user_id),
            "timezone": timezone,
            "language": language,
        }

        # Consume the stream; keep the latest state with a terminal status.
        last_terminal: dict[str, Any] | None = None
        async for values in self._graph.astream(
            inputs, config=config, stream_mode="values"
        ):
            if values.get("status") in _TERMINAL_STATUSES:
                last_terminal = values

        # If the graph stopped on an interrupt (HITL), the checkpoint holds the pause.
        if last_terminal is None:
            state = await self._graph.aget_state(config)
            if state and state.next:
                last_terminal = dict(state.values or {})
                last_terminal["status"] = "awaiting_confirmation"

        if last_terminal is not None:
            yield self._final_payload(last_terminal)

    async def resume(
        self,
        *,
        user_id: UUID,
        thread_id: str,
        approved: bool,
    ) -> AsyncIterator[dict[str, Any]]:
        assert self._graph is not None
        config = self._thread_config(user_id, thread_id)

        last_terminal: dict[str, Any] | None = None
        async for values in self._graph.astream(
            Command(resume=approved), config=config, stream_mode="values"
        ):
            if values.get("status") in _TERMINAL_STATUSES:
                last_terminal = values

        if last_terminal is not None:
            yield self._final_payload(last_terminal)


# ─── Singleton managed in main.py lifespan ─────────────
_agent_service: AgentService | None = None


def get_agent_service() -> AgentService:
    global _agent_service
    if _agent_service is None:
        _agent_service = AgentService()
    return _agent_service
