"""Node: ask the user to disambiguate when intent is unclear."""


from __future__ import annotations


from app.agent.state import AgentState




async def resolve_ambiguity(state: AgentState) -> AgentState:
    """Called when parse_intent flags ambiguity.


    In V1, we emit a clarification question + options to the UI via SSE.
    The graph stops here (interrupt); it resumes once the user replies.
    """
    state["status"] = "awaiting_clarification"
    return state
