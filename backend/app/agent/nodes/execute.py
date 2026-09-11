"""Node: execute planned actions and record audit logs."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from app.agent.state import AgentState
from app.db.session import get_session_factory
from app.repositories.event_repository import EventRepository
from app.services.calendar_service import CalendarService


_TOOL_REGISTRY: dict[str, Any] = {}


def _register() -> None:
    from app.agent.tools.calendar_tools import create_event, delete_event, list_events, update_event
    from app.agent.tools.scheduling_tools import find_free_slots
    _TOOL_REGISTRY.update({"list_events": list_events, "create_event": create_event, "update_event": update_event, "delete_event": delete_event, "find_free_slots": find_free_slots})


async def _resolve_event_id(user_id: UUID, query: str) -> str | None:
    factory = get_session_factory()
    async with factory() as db:
        now = datetime.now().astimezone()
        events = await EventRepository(db).list_in_range(user_id, now - timedelta(days=30), now + timedelta(days=90))
        q = query.lower().strip()
        for e in events:
            if q in e.summary.lower():
                return e.google_event_id
    return None


async def execute(state: AgentState) -> AgentState:
    if not _TOOL_REGISTRY:
        _register()
    user_id = UUID(state["user_id"])
    actions = state.get("planned_actions", [])
    results: list[dict[str, Any]] = []

    for action in actions:
        tool_name = action["tool"]
        args = dict(action["args"])
        if tool_name == "bulk_cancel":
            from datetime import datetime as _dt
            start = _dt.fromisoformat(args["date_range_start"])
            end = _dt.fromisoformat(args["date_range_end"])
            factory = get_session_factory()
            async with factory() as db:
                events = await EventRepository(db).list_in_range(user_id, start, end)
                svc = CalendarService(db)
                for e in events:
                    try:
                        await svc.delete_event(user_id, e.google_event_id)
                        results.append({"tool": "delete_event", "status": "ok", "id": e.google_event_id})
                    except Exception as exc:
                        results.append({"tool": "delete_event", "status": "error", "error": str(exc)})
                await db.commit()
            continue
        if tool_name in ("update_event", "delete_event") and "event_query" in args:
            query = args.pop("event_query")
            gid = await _resolve_event_id(user_id, query)
            if not gid:
                results.append({"tool": tool_name, "status": "not_found", "query": query})
                continue
            args["google_event_id"] = gid
        tool = _TOOL_REGISTRY.get(tool_name)
        if tool is None:
            results.append({"tool": tool_name, "status": "unknown_tool"})
            continue
        try:
            output = await tool.ainvoke(args, config={"configurable": {"user_id": str(user_id)}})
            results.append({"tool": tool_name, "status": "ok", "output": output})
        except Exception as e:
            results.append({"tool": tool_name, "status": "error", "error": str(e)})

    state["tool_results"] = results
    state["status"] = "done"
    return state
