"""LangGraph workflow for the chronos-agent."""


from __future__ import annotations


from typing import TYPE_CHECKING

from langgraph.graph import END, START, StateGraph

if TYPE_CHECKING:
    from langgraph.graph.state import CompiledStateGraph

from app.agent.nodes.execute import execute
from app.agent.nodes.human_confirm import human_confirm
from app.agent.nodes.parse_intent import parse_intent
from app.agent.nodes.plan_tools import plan_tools
from app.agent.nodes.respond import respond
from app.agent.nodes.resolve_ambiguity import resolve_ambiguity
from app.agent.state import AgentState
from app.llm import LLMProvider, build_llm_provider


def _route_after_parse(state: AgentState) -> str:
    if state.get("clarification_needed"):
        return "resolve_ambiguity"
    return "plan_tools"


def _route_after_plan(state: AgentState) -> str:
    if state.get("requires_confirmation"):
        return "human_confirm"
    return "execute"


def build_graph(llm: LLMProvider | None = None):
    provider = llm or build_llm_provider()

    async def _parse(state: AgentState) -> AgentState:
        return await parse_intent(state, llm=provider)

    graph = StateGraph(AgentState)

    graph.add_node("parse_intent", _parse)
    graph.add_node("resolve_ambiguity", resolve_ambiguity)
    graph.add_node("plan_tools", plan_tools)
    graph.add_node("human_confirm", human_confirm)
    graph.add_node("execute", execute)
    graph.add_node("respond", respond)

    graph.add_edge(START, "parse_intent")
    graph.add_conditional_edges(
        "parse_intent",
        _route_after_parse,
        {"resolve_ambiguity": "resolve_ambiguity", "plan_tools": "plan_tools"},
    )
    graph.add_conditional_edges(
        "plan_tools",
        _route_after_plan,
        {"human_confirm": "human_confirm", "execute": "execute"},
    )
    graph.add_edge("resolve_ambiguity", END)
    graph.add_edge("human_confirm", END)
    graph.add_edge("execute", "respond")
    graph.add_edge("respond", END)

    return graph.compile()
