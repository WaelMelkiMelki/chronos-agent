# 5. Self-hosted SaaS, MCP in V2


- Status: Accepted
- Date: 2026-09-10


## Context
The project targets a multi-user SaaS architecture but must remain
100% local with zero budget. MCP is desirable but adds surface area.


## Decision
- Architecture is **SaaS-ready**: JWT auth, per-user data isolation,
  OAuth token storage per user, quotas.
- Deployment model is **self-hosted** via `docker compose up`.
- **MCP** servers (Calendar, Memory, Documents) are introduced in V2.
  V1 tools are plain Python functions wrapped as LangGraph tools.


## Rationale
- "SaaS-ready + self-hosted" gives the CV the best of both worlds
  without the cost/complexity of a real hosted SaaS.
- MCP is powerful but not required to prove the agent concept.


## Consequences
- No public hosted demo; demo is a screen recording.
- Token storage security is critical (Fernet encryption).
- V2 will wrap the same domain services behind MCP servers.
