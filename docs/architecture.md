# Architecture

> This document will be expanded as the project evolves.
> See [docs/adr/](adr/) for individual decision records.

## High-level overview

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Frontend   │────▶│    Backend    │────▶│  PostgreSQL  │
│  (Next.js)   │     │  (FastAPI)    │     │             │
└─────────────┘     └──────┬───────┘     └─────────────┘
                           │
                    ┌──────▼───────┐
                    │   LangGraph   │
                    │    Agent      │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ Calendar  │ │  LLM     │ │  Audit   │
        │  Tools    │ │ Provider │ │  Log     │
        └──────────┘ └──────────┘ └──────────┘
```

## Tech stack

| Layer     | Technology          |
|-----------|---------------------|
| Frontend  | Next.js 15, Tailwind CSS, shadcn/ui |
| Backend   | Python 3.12, FastAPI, SQLAlchemy 2 (async), Alembic |
| Agent     | LangGraph, LangChain tool wrappers |
| Database  | PostgreSQL 16       |
| LLM       | Ollama (local) / Groq / Gemini |
| Vector DB | Qdrant (V2 only)    |
| Auth      | JWT + Google OAuth2  |
| Deploy    | Docker Compose       |

## Layers

### Backend (`backend/app/`)

- **`core/`** — config, security, dependencies, exceptions
- **`api/v1/`** — FastAPI routers (auth, calendar, agent, audit, settings)
- **`models/`** — SQLAlchemy ORM models
- **`schemas/`** — Pydantic request/response schemas
- **`repositories/`** — data access layer
- **`services/`** — business logic
- **`agent/`** — LangGraph graph, state, nodes
- **`llm/`** — LLM provider abstraction
- **`integrations/`** — external APIs (Google Calendar)

### Frontend (`frontend/src/`)

- `app/` — Next.js App Router pages
- `components/` — UI components (shadcn/ui based)
- `lib/` — API client, hooks, utilities
- `i18n/` — FR/EN translations
