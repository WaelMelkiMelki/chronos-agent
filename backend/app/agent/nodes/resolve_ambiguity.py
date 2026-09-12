"""Node: surface a clarification question to the user."""

from __future__ import annotations

from app.agent.state import AgentState


async def resolve_ambiguity(state: AgentState) -> AgentState:
    """Set status + final_response so the frontend displays the question."""
    question = state.get("clarification_question") or (
        "Peux-tu préciser ta demande ?"
    )
    state["status"] = "awaiting_clarification"
    state["final_response"] = question
    return state
