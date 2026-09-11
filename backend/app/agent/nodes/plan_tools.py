"""Node: map parsed intent → list of pending actions."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from app.agent.state import AgentState, PendingAction


def _iso(value: Any) -> str | None:
    if value is None: return None
    if isinstance(value, str): return value
    if isinstance(value, datetime): return value.isoformat()
    return str(value)


def _preview(intent: str, args: dict[str, Any]) -> str:
    if intent == "create_event": return f"Créer « {args.get('summary', '?')} » le {args.get('start', '?')}"
    if intent == "update_event": return f"Modifier « {args.get('event_query', '?')} »"
    if intent == "delete_event": return f"Supprimer « {args.get('event_query', '?')} »"
    if intent == "find_free_slots": return f"Chercher un créneau de {args.get('duration_minutes', '?')} min entre {args.get('range_start', '?')} et {args.get('range_end', '?')}"
    if intent == "bulk_cancel": return f"Annuler tous les rendez-vous du {args.get('date_range_start', '?')} au {args.get('date_range_end', '?')}"
    return "Action inconnue"


async def plan_tools(state: AgentState) -> AgentState:
    intent = state.get("intent", "unknown")
    args = state.get("parsed_args", {})
    actions: list[PendingAction] = []

    if intent == "list_events":
        actions.append({"tool": "list_events", "args": {"start": args.get("start") or datetime.now().isoformat(), "end": args.get("end") or (datetime.now() + timedelta(days=7)).isoformat()}, "preview": "Lister les événements"})
        state["requires_confirmation"] = False
    elif intent == "find_free_slots":
        actions.append({"tool": "find_free_slots", "args": args, "preview": _preview(intent, args)})
        state["requires_confirmation"] = False
    elif intent == "create_event":
        actions.append({"tool": "create_event", "args": args, "preview": _preview(intent, args)})
        state["requires_confirmation"] = True
    elif intent == "update_event":
        actions.append({"tool": "update_event", "args": args, "preview": _preview(intent, args)})
        state["requires_confirmation"] = True
    elif intent == "delete_event":
        actions.append({"tool": "delete_event", "args": args, "preview": _preview(intent, args)})
        state["requires_confirmation"] = True
    elif intent == "bulk_cancel":
        actions.append({"tool": "bulk_cancel", "args": args, "preview": _preview(intent, args)})
        state["requires_confirmation"] = True

    state["planned_actions"] = actions
    return state
