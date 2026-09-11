# 3. LLM provider abstraction


- Status: Accepted
- Date: 2026-09-10


## Context
Constraints:
- Local-first by default (privacy).
- Developer machine: i5, 16 GB RAM, no GPU.
- Zero budget, no payment card.
- User must be able to plug in a token for a remote provider.


## Decision
Introduce an `LLMProvider` abstract base class with concrete
implementations:
- `OllamaProvider` (default, local)
- `GroqProvider` (free cloud, fast)
- `GeminiProvider` (free cloud, fallback)
- `OpenAICompatibleProvider` (any OpenAI-compatible endpoint)


A `LLMFactory` selects the provider from settings stored per user.


## Defaults
- Dev / demo: `ollama` + `qwen3:4b` (Q4) for CPU-only machines.
- Cloud fallback: `groq` + `llama-3.3-70b-versatile`.


## Consequences
- Provider-agnostic agent code.
- Extra abstraction layer to maintain.
- Easy to add new providers (Anthropic, Mistral, etc.).
