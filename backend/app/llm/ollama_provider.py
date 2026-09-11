from langchain_ollama import ChatOllama


from app.core.config import get_settings
from app.llm.base import LLMProvider




class OllamaProvider(LLMProvider):
    name = "ollama"


    def __init__(self, model: str | None = None) -> None:
        settings = get_settings()
        self._model = model or settings.llm_model
        self._base_url = settings.ollama_base_url


    def chat_model(self) -> ChatOllama:
        return ChatOllama(
            model=self._model,
            base_url=self._base_url,
            temperature=0.1,
        )
