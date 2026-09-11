"""Node: execute the planned tool calls and record audit logs."""


from __future__ import annotations


from app.agent.state import AgentState


async def execute(state: AgentState) -> AgentState:
    actions = state.get("planned_actions", [])
    results: list[dict] = []

    for action in actions:
        # TODO: dispatch to the registry of tools, capture result,
        # write an audit_log row via AuditService.
        # TODO(phase-4): audit
        results.append({"tool": action["tool"], "status": "not_implemented"})

    state["tool_results"] = results
    state["status"] = "done"
    return state
