# 2. Use LangGraph for agent orchestration


- Status: Accepted
- Date: 2026-09-10


## Context
The agent must:
- Parse user intent (natural language, FR/EN)
- Call tools (calendar, scheduling, audit)
- Ask for confirmation before mutating actions (human-in-the-loop)
- Handle ambiguity by presenting options
- Support resumable/checkpointed execution


Candidates: LangChain agents, CrewAI, AutoGen, custom FSM, LangGraph.


## Decision
Use **LangGraph**.


## Rationale
- Explicit graph = testable nodes, clear control flow.
- First-class support for **interrupt / resume** (HITL).
- Native checkpointing (state persistence in Postgres later).
- Compatible with MCP tools.
- More production-oriented than CrewAI.


## Consequences
- Learning curve for StateGraph, reducers, checkpointers.
- Tied to LangChain ecosystem for tool wrappers (acceptable).
