"""Node: choose concrete tool calls from the parsed intent."""


from __future__ import annotations


from app.agent.state import AgentState




async def plan_tools(state: AgentState) -> AgentState:
    intent = state.get("intent", "unknown")
    args = state.get("parsed_args", {})


    # TODO: map intent → tool + args, fill state["planned_actions"]
    # Example:
    # if intent == "update_event":
    #     state["planned_actions"] = [{
    #         "tool": "update_event",
    #         "args": args,
    #         "preview": "...",
    #     }]
    state["planned_actions"] = state.get("planned_actions", [])
    state["requires_confirmation"] = True
    return state
