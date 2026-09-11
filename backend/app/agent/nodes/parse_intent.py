"""Node: convert free-form user text into a structured intent."""

from __future__ import annotations

import json
import re
from typing import Any
from datetime import datetime

from langchain_core.messages import HumanMessage, SystemMessage

from app.agent.state import AgentState
from app.llm.base import LLMProvider


_SYSTEM = """You are the intent parser of a calendar assistant.
Today is {now} ({weekday}). The user's timezone is {tz}.

Return STRICT JSON only (no prose, no markdown):
{{
  "intent": "list_events" | "create_event" | "update_event" |
            "delete_event" | "find_free_slots" | "bulk_cancel" | "unknown",
  "args": {{ ... }},
  "ambiguous": true | false,
  "clarification_question": "..." | null
}}

Arg conventions:
- create_event: {{summary, start, end, description?, location?, all_day?}}
  dates in ISO 8601 with offset, e.g. 2026-09-11T15:00:00+02:00
- update_event: {{event_query, new_start?, new_end?, new_summary?}}
- delete_event: {{event_query}}
- find_free_slots: {{range_start, range_end, duration_minutes}}
- bulk_cancel: {{date_range_start, date_range_end}}

If the request is missing a critical field, set "ambiguous": true and
provide a clarification_question.
"""


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    fence = re.match(r"^```(?:json)?\s*(.+?)\s*```$", text, re.DOTALL)
    if fence:
        text = fence.group(1)
    return json.loads(text)


async def parse_intent(state: AgentState, *, llm: LLMProvider) -> AgentState:
    user_text = state.get("raw_user_input", "")
    tz = state.get("timezone", "UTC")
    now = datetime.now().isoformat(timespec="minutes")

    messages = [
        SystemMessage(content=_SYSTEM.format(now=now, weekday="", tz=tz)),
        HumanMessage(content=user_text),
    ]

    response = await llm.ainvoke(messages)
    content = response.content if isinstance(response.content, str) else str(response.content)

    try:
        parsed = _extract_json(content)
    except (json.JSONDecodeError, ValueError):
        state["intent"] = "unknown"
        state["parsed_args"] = {}
        state["clarification_needed"] = True
        state["clarification_question"] = "Je n'ai pas compris. Peux-tu reformuler ta demande ?"
        state["status"] = "parsing"
        return state

    state["intent"] = parsed.get("intent", "unknown")
    state["parsed_args"] = parsed.get("args", {}) or {}
    state["clarification_needed"] = bool(parsed.get("ambiguous"))
    state["clarification_question"] = parsed.get("clarification_question")
    state["status"] = "parsing"
    return state
