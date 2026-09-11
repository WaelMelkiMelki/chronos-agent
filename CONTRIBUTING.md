# Contributing to chronos-agent

Thank you for considering contributing!

## Development setup

```bash
cp .env.example .env
docker compose -f docker-compose.dev.yml up -d
```

## Branches

- `main` — production-ready
- `develop` — integration branch
- `feat/*` — feature branches
- `fix/*` — bugfix branches

## Commits

We use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat: add calendar sync`
- `fix: resolve timezone offset`
- `chore: update dependencies`
- `docs: update ADR 003`

## Pull requests

1. Branch from `develop`
2. Keep PRs small and focused
3. Include tests when applicable
4. Update docs if behavior changes

## Code style

- Python: Ruff (lint + format), mypy (type check)
- TypeScript: ESLint + Prettier
- Always run linters before committing

## ADRs

For architectural decisions, create an ADR in `docs/adr/` following the format in `0001-record-architecture-decisions.md`.
