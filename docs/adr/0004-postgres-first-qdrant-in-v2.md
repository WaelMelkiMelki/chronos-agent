# 4. Postgres first, Qdrant in V2


- Status: Accepted
- Date: 2026-09-10


## Context
Qdrant was initially considered for the MVP for memory / semantic
search. But the MVP scope is: chat → agent → calendar → audit.


## Decision
- V1: **PostgreSQL only**.
- Qdrant introduced in **V2** behind the `FEATURE_QDRANT` flag, for:
  - Document RAG (CV, notes).
  - Semantic memory of user preferences.
  - Conversation recall.


## Rationale
- Avoid premature infrastructure.
- Postgres handles users, events cache, audit logs, settings.
- Qdrant adds value only once RAG / memory is needed.


## Consequences
- Less infra in V1 (faster iteration).
- Migration path planned: `memory/` module exposes an interface,
  Postgres-backed in V1, Qdrant-backed in V2.
