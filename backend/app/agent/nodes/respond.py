"""Node: produce the final natural-language response to the user."""


from __future__ import annotations


from app.agent.state import AgentState




async def respond(state: AgentState) -> AgentState:
    results = state.get("tool_results", [])
    state["final_response"] = (
        f"Done. {len(results)} action(s) executed."
        if results
        else "No actions executed."
    )
    return state
