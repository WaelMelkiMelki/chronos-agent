from langchain_groq import ChatGroq


from app.core.config import get_settings
from app.llm.base import LLMProvider




class GroqProvider(LLMProvider):
    name = "groq"


    def __init__(self, model: str | None = None, api_key: str | None = None) -> None:
        settings = get_settings()
        self._model = model or settings.groq_model
        self._api_key = api_key or settings.groq_api_key
        if not self._api_key:
            raise ValueError("GROQ_API_KEY is required for the groq provider")


    def chat_model(self) -> ChatGroq:
        return ChatGroq(
            model=self._model,
            api_key=self._api_key,  # type: ignore[arg-type]
            temperature=0.1,
        )
