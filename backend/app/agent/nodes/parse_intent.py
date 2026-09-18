"""Node: convert free-form user text into a structured intent."""

from __future__ import annotations

import json
import re
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from app.agent.state import AgentState
from app.llm.base import LLMProvider

_SYSTEM = """You are the intent parser of a calendar assistant.
Today is {now} (weekday {weekday}). The user's timezone is {tz}.

CRITICAL: All datetime outputs must use the user's timezone offset,
NOT UTC. Example: if the user's timezone is Africa/Tunis (UTC+1) and
the user says "demain à 15h", the output must be
"2026-09-13T15:00:00+01:00".

Return STRICT JSON only (no prose, no markdown, no code fences):
{{
  "intent": "list_events" | "create_event" | "update_event" |
            "delete_event" | "find_free_slots" | "bulk_cancel" | "unknown",
  "args": {{ ... }},
  "ambiguous": true | false,
  "clarification_question": "..." | null
}}

Arg conventions:
- create_event:   {{summary, start, end, description?, location?, all_day?}}
- update_event:   {{event_query, new_start?, new_end?, new_summary?}}
- delete_event:   {{event_query}}
- find_free_slots:{{range_start, range_end, duration_minutes}}
- bulk_cancel:    {{date_range_start, date_range_end}}

Dates must be ISO 8601 with an offset, e.g. 2026-09-11T15:00:00+02:00.

DEFAULTS — apply these yourself, DO NOT ask for clarification:
- create_event: if "end" is missing, default to start + 60 minutes.
- create_event: if "summary" is missing but the user clearly names a topic,
  reuse their words as the summary.
- find_free_slots: if "range_start"/"range_end" are missing, use today and
  today+7 days, at 09:00 and 18:00 in the user's timezone.

Only set "ambiguous": true if a CRITICAL field is impossible to infer
(e.g. no date at all for create_event, or the user mentions an event
with no way to identify it for update/delete). When ambiguous, put a
SHORT question in "clarification_question" (max 1 sentence, in the
user's language).
"""


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    fence = re.match(r"^```(?:json)?\s*(.+?)\s*```$", text, re.DOTALL)
    if fence:
        text = fence.group(1)
    return json.loads(text)


async def parse_intent(state: AgentState, *, llm: LLMProvider) -> AgentState:
    from datetime import datetime

    user_text = state.get("raw_user_input", "")
    tz = state.get("timezone", "UTC")
    now_dt = datetime.now()
    now = now_dt.isoformat(timespec="minutes")
    weekday = now_dt.strftime("%A")

    messages = [
        SystemMessage(content=_SYSTEM.format(now=now, weekday=weekday, tz=tz)),
        HumanMessage(content=user_text),
    ]

    response = await llm.ainvoke(messages)
    content = (
        response.content if isinstance(response.content, str) else str(response.content)
    )

    # reasoning models (e.g. gpt-oss) sometimes emit reasoning + JSON; keep last JSON
    try:
        parsed = _extract_json(content)
    except (json.JSONDecodeError, ValueError):
        # try to find the last {...} block
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            try:
                parsed = json.loads(match.group(0))
            except json.JSONDecodeError:
                parsed = None
        else:
            parsed = None

    if parsed is None:
        state["intent"] = "unknown"
        state["parsed_args"] = {}
        state["clarification_needed"] = True
        state["clarification_question"] = (
            "Je n'ai pas compris. Peux-tu reformuler ta demande ?"
        )
        state["status"] = "parsing"
        return state

    state["intent"] = parsed.get("intent", "unknown")
    state["parsed_args"] = parsed.get("args", {}) or {}
    state["clarification_needed"] = bool(parsed.get("ambiguous"))
    state["clarification_question"] = parsed.get("clarification_question")
    state["status"] = "parsing"
    return state
