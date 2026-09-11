"""Node: convert free-form user text into a structured intent."""


from __future__ import annotations


from langchain_core.messages import HumanMessage, SystemMessage


from app.agent.state import AgentState
from app.llm.base import LLMProvider


_SYSTEM_PROMPT = """You are an intent classifier for a calendar assistant.
Return STRICT JSON matching this schema:
{
  "intent": "list_events" | "create_event" | "update_event" |
            "delete_event" | "find_free_slots" | "bulk_cancel" | "unknown",
  "args": { ... intent-specific arguments ... },
  "ambiguous": true | false,
  "clarification_question": "..." | null
}
Do NOT include explanations, markdown, or code fences. JSON only.
"""




async def parse_intent(state: AgentState, *, llm: LLMProvider) -> AgentState:
    user_text = state.get("raw_user_input", "")
    messages = [
        SystemMessage(content=_SYSTEM_PROMPT),
        HumanMessage(content=user_text),
    ]


    response = await llm.ainvoke(messages)
    # TODO: parse JSON, populate state["intent"], state["parsed_args"],
    # state["clarification_needed"], etc.
    # Placeholder: keep state unchanged for now.
    state["status"] = "parsing"
    return state
