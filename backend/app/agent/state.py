"""Agent state — the single source of truth across LangGraph nodes."""


from __future__ import annotations


from typing import Annotated, Any, Literal, TypedDict


from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


IntentType = Literal[
    "list_events",
    "create_event",
    "update_event",
    "delete_event",
    "find_free_slots",
    "bulk_cancel",
    "unknown",
]


AgentStatus = Literal[
    "parsing",
    "awaiting_clarification",
    "awaiting_confirmation",
    "executing",
    "done",
    "error",
]




class ClarificationOption(TypedDict):
    id: str
    label: str
    payload: dict[str, Any]




class PendingAction(TypedDict):
    tool: str
    args: dict[str, Any]
    preview: str  # human-readable summary for the confirm card




class AgentState(TypedDict, total=False):
    # Conversation
    messages: Annotated[list[BaseMessage], add_messages]


    # Context
    user_id: str
    timezone: str
    language: str  # "fr" | "en"


    # Parsing
    intent: IntentType
    raw_user_input: str
    parsed_args: dict[str, Any]


    # Ambiguity
    clarification_needed: bool
    clarification_question: str | None
    clarification_options: list[ClarificationOption]


    # Planning
    planned_actions: list[PendingAction]
    requires_confirmation: bool


    # Execution
    status: AgentStatus
    tool_results: list[dict[str, Any]]
    error: str | None


    # Response
    final_response: str | None
