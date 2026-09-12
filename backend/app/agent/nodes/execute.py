"""Node: execute planned actions and record audit logs."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from app.agent.state import AgentState
from app.db.session import get_session_factory
from app.services.calendar_service import CalendarService

_TOOL_REGISTRY: dict[str, Any] = {}

# TODO(phase-4): wire audit logging here


def _register() -> None:
    """Import tools lazily to avoid import cycles at module load."""
    from app.agent.tools.calendar_tools import (
        create_event,
        delete_event,
        list_events,
        update_event,
    )
    from app.agent.tools.scheduling_tools import find_free_slots

    _TOOL_REGISTRY.update(
        {
            "list_events": list_events,
            "create_event": create_event,
            "update_event": update_event,
            "delete_event": delete_event,
            "find_free_slots": find_free_slots,
        }
    )


async def _call_tool(tool: Any, args: dict[str, Any], user_id: UUID) -> Any:
    """Call a LangChain tool with user_id injected via RunnableConfig.

    We validate args through the tool's Pydantic schema first, so that
    fields typed as `datetime` are actually datetime objects (not ISO
    strings), then we call the underlying coroutine directly because
    BaseTool.ainvoke does not forward RunnableConfig to the function's
    `config` parameter in the installed langchain-core version.
    """
    schema = getattr(tool, "args_schema", None)
    if schema is not None:
        coerced = schema.model_validate(args).model_dump()
    else:
        coerced = dict(args)

    config = {"configurable": {"user_id": str(user_id)}}

    coroutine = getattr(tool, "coroutine", None)
    if coroutine is not None:
        return await coroutine(**coerced, config=config)

    func = getattr(tool, "func", None)
    if func is not None:
        return func(**coerced, config=config)

    raise RuntimeError(f"Tool {getattr(tool, 'name', '?')} has no callable")

async def _resolve_event_id(user_id: UUID, query: str) -> str | None:
    """Very basic fuzzy match: first event whose summary contains the query."""
    from datetime import timedelta

    from app.repositories.event_repository import EventRepository

    factory = get_session_factory()
    async with factory() as db:
        now = datetime.now().astimezone()
        events = await EventRepository(db).list_in_range(
            user_id, now - timedelta(days=30), now + timedelta(days=90)
        )
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
            results.extend(await _run_bulk_cancel(user_id, args))
            continue

        if tool_name in ("update_event", "delete_event") and "event_query" in args:
            query = args.pop("event_query")
            gid = await _resolve_event_id(user_id, query)
            if not gid:
                results.append(
                    {"tool": tool_name, "status": "not_found", "query": query}
                )
                continue
            args["google_event_id"] = gid

        tool = _TOOL_REGISTRY.get(tool_name)
        if tool is None:
            results.append({"tool": tool_name, "status": "unknown_tool"})
            continue

        try:
            output = await _call_tool(tool, args, user_id)
            results.append({"tool": tool_name, "status": "ok", "output": output})
        except Exception as e:  # noqa: BLE001
            results.append({"tool": tool_name, "status": "error", "error": str(e)})

    state["tool_results"] = results
    state["status"] = "done"
    return state


async def _run_bulk_cancel(
    user_id: UUID, args: dict[str, Any]
) -> list[dict[str, Any]]:
    from datetime import timedelta

    from app.repositories.event_repository import EventRepository

    start = datetime.fromisoformat(args["date_range_start"])
    end = datetime.fromisoformat(args["date_range_end"])
    factory = get_session_factory()
    out: list[dict[str, Any]] = []
    async with factory() as db:
        events = await EventRepository(db).list_in_range(user_id, start, end)
        svc = CalendarService(db)
        for e in events:
            try:
                await svc.delete_event(user_id, e.google_event_id)
                out.append(
                    {"tool": "delete_event", "status": "ok", "id": e.google_event_id}
                )
            except Exception as exc:  # noqa: BLE001
                out.append(
                    {"tool": "delete_event", "status": "error", "error": str(exc)}
                )
        await db.commit()
    _ = timedelta
    return out
