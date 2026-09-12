# chronos-agent

> Agent IA local-first, multi-utilisateurs, qui gère votre calendrier
> en langage naturel (FR / EN).

[![Backend CI](https://github.com/wael-melki/chronos-agent/actions/workflows/backend-ci.yml/badge.svg)](https://github.com/wael-melki/chronos-agent/actions/workflows/backend-ci.yml)
[![Frontend CI](https://github.com/wael-melki/chronos-agent/actions/workflows/frontend-ci.yml/badge.svg)](https://github.com/wael-melki/chronos-agent/actions/workflows/frontend-ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Fonctionnalités (MVP)

- Multi-utilisateurs avec JWT + OAuth2 Google
- Google Calendar : lecture / création / modification / suppression d'événements
- Agent LangGraph avec function calling + human-in-the-loop (confirmation avant chaque action)
- Planification intelligente : heures de bureau, pause déjeuner, buffers, sans chevauchement
- Journal d'audit des actions de l'agent (undo / rollback)
- i18n FR / EN
- LLM local (Ollama) ou cloud gratuit (Groq / Gemini)
- Docker Compose en une commande

## Démarrage rapide

```bash
cp .env.example .env
# renseigner GOOGLE_CLIENT_ID/SECRET et FERNET_KEY
docker compose up -d
# ouvrir http://localhost:3000
```

## Architecture

Voir [docs/architecture.md](docs/architecture.md) et [docs/adr/](docs/adr/).

## Roadmap

- **v0.1.0** — MVP (ce repo)
- **v0.2.0** — Qdrant + RAG sur documents / CV
- **v0.3.0** — Serveurs MCP (Calendar, Memory, Documents)

## Licence

MIT — voir [LICENSE](LICENSE).
