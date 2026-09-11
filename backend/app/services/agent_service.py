"""AgentService: orchestrates the LangGraph agent and streams SSE events."""


from __future__ import annotations


import json
import uuid
from collections.abc import AsyncIterator
from typing import Any

from langchain_core.messages import HumanMessage

from app.agent.graph import build_graph
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class AgentService:
    _graph: Any | None = None
    _saver: Any | None = None

    @classmethod
    async def initialize(cls) -> None:
        """Create the graph. Postgres checkpointing is optional
        and requires langgraph-checkpoint-postgres >= 2.x with
        a working AsyncPostgresSaver implementation."""
        settings = get_settings()
        dsn = settings.database_url.replace("postgresql+asyncpg://", "postgresql://", 1)
        try:
            from langgraph.checkpoint.postgres import PostgresSaver
            cm = PostgresSaver.from_conn_string(dsn)
            saver = cm.__enter__()
            saver.setup()
            cls._saver = saver
        except Exception as e:
            logger.warning("PostgresSaver not available (check langgraph-checkpoint-postgres version): %s", e)
        # Compile without checkpointer to avoid
        # aget_tuple NotImplementedError on some versions.
        cls._graph = build_graph()

    @classmethod
    def get_graph(cls) -> Any:
        if cls._graph is None:
            raise RuntimeError("AgentService not initialized. Call initialize() first.")
        return cls._graph

    async def run(self, message: str, thread_id: str | None = None) -> AsyncIterator[dict[str, Any]]:
        """Stream the agent graph and emit SSE-compatible events.

        Uses graph.astream() for compatibility regardless of
        checkpoint provider version. After streaming completes,
        emits a final event with the computed state.
        """
        graph = self.get_graph()
        if thread_id is None:
            thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        initial_state = {
            "messages": [HumanMessage(content=message)],
            "user_id": "todo-user-id",
            "timezone": "Europe/Paris",
            "language": "fr",
            "status": "parsing",
        }

        final_values: dict[str, Any] = {}
        async for event in graph.astream(initial_state, config=config):
            if isinstance(event, dict):
                node_name = list(event.keys())[0] if event else ""
                node_values = event.get(node_name, {}) if node_name else {}
                final_values = node_values
                if node_name == "parse_intent":
                    yield self._sse_event("status", {"status": "parsing"})
                elif node_name == "plan_tools":
                    yield self._sse_event("status", {"status": "executing"})
                elif node_name == "human_confirm":
                    yield self._sse_event("status", {"status": "awaiting_confirmation"})
                elif node_name == "execute":
                    yield self._sse_event("status", {"status": "executing"})
                elif node_name == "respond":
                    yield self._sse_event("status", {"status": "done"})

        yield self._sse_event("final", {
            "status": final_values.get("status", "done"),
            "intent": final_values.get("intent"),
            "planned_actions": final_values.get("planned_actions", []),
            "tool_results": final_values.get("tool_results", []),
            "final_response": final_values.get("final_response"),
        })

    @staticmethod
    def _sse_event(event_type: str, data: dict[str, Any]) -> dict[str, Any]:
        return {"event": event_type, "data": data}
