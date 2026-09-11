<<<<<<< HEAD
# chronos-agent

> Local-first, multi-user AI agent that manages your calendar
> from natural language (FR / EN).

[![Backend CI](https://github.com/wael-melki/chronos-agent/actions/workflows/backend-ci.yml/badge.svg)](https://github.com/wael-melki/chronos-agent/actions/workflows/backend-ci.yml)
[![Frontend CI](https://github.com/wael-melki/chronos-agent/actions/workflows/frontend-ci.yml/badge.svg)](https://github.com/wael-melki/chronos-agent/actions/workflows/frontend-ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Features (MVP)

- Multi-user with JWT + Google OAuth2
- Google Calendar read / create / update / delete
- LangGraph agent with function calling + human-in-the-loop
- Smart scheduling: office hours, lunch, buffers, no-overlap
- Audit log + undo / rollback
- i18n FR / EN
- Local LLM (Ollama) or free cloud LLM (Groq / Gemini)
- One-command Docker Compose

## Quick start

```bash
cp .env.example .env
# fill in GOOGLE_CLIENT_ID/SECRET and FERNET_KEY
docker compose up -d
# open http://localhost:3000
```

## Architecture

See [docs/architecture.md](docs/architecture.md) and [docs/adr/](docs/adr/).

## Roadmap

- **v0.1.0** — MVP (this repo)
- **v0.2.0** — Qdrant + RAG on documents / CV
- **v0.3.0** — MCP servers (Calendar, Memory, Documents)

## License

MIT — see [LICENSE](LICENSE).
# chronos-agent
=======
# chronos-agent
>>>>>>> a29aa6b019776140b8bb45cee5840e9500435fec
