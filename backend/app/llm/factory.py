from app.core.config import get_settings
from app.llm.base import LLMProvider
from app.llm.gemini_provider import GeminiProvider
from app.llm.groq_provider import GroqProvider
from app.llm.ollama_provider import OllamaProvider


_PROVIDERS: dict[str, type[LLMProvider]] = {
    "ollama": OllamaProvider,
    "groq": GroqProvider,
    "gemini": GeminiProvider,
}




def build_llm_provider(
    provider: str | None = None,
    model: str | None = None,
    api_key: str | None = None,
) -> LLMProvider:
    """Resolve provider from explicit args or settings."""
    settings = get_settings()
    name = (provider or settings.llm_provider).lower()


    if name not in _PROVIDERS:
        raise ValueError(f"Unknown LLM provider: {name!r}")


    cls = _PROVIDERS[name]


    if name == "ollama":
        return OllamaProvider(model=model)
    if name == "groq":
        return GroqProvider(model=model, api_key=api_key)
    if name == "gemini":
        return GeminiProvider(model=model, api_key=api_key)
    raise ValueError(f"Unhandled provider: {name}")
