"""Node: pause the graph and wait for user confirmation (HITL)."""


from __future__ import annotations


from langgraph.types import interrupt

from app.agent.state import AgentState


async def human_confirm(state: AgentState) -> AgentState:
    """Interrupt point: UI shows a confirmation card.

    LangGraph `interrupt()` pauses the graph and waits for the user
    to respond before the graph resumes.
    """
    interrupt("Waiting for user confirmation before executing planned actions.")
    state["status"] = "awaiting_confirmation"
    return state
