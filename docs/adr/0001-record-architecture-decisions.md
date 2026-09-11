# 1. Record architecture decisions


- Status: Accepted
- Date: 2026-09-10


## Context
We need a lightweight, versioned way to capture why significant
technical decisions were made in chronos-agent.


## Decision
We use Architecture Decision Records (ADRs) in the format proposed
by Michael Nygard. Each ADR lives in `docs/adr/` and is immutable
once accepted. Superseding is done via a new ADR.


## Consequences
- Onboarding is faster.
- Reviews have historical context.
- Slight overhead for each non-trivial decision.
