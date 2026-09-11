"""Node: pause the graph and wait for user confirmation (HITL)."""

from __future__ import annotations

from langgraph.types import interrupt
from app.agent.state import AgentState


async def human_confirm(state: AgentState) -> AgentState:
    payload = {
        "question": "Confirmer cette action ?",
        "actions": [{"tool": a["tool"], "preview": a["preview"]} for a in state.get("planned_actions", [])],
    }
    approved = interrupt(payload)
    if not approved:
        state["status"] = "done"
        state["tool_results"] = [{"status": "cancelled_by_user"}]
        state["planned_actions"] = []
        state["final_response"] = "Action annulée."
    return state
