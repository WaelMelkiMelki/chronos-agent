from langchain_google_genai import ChatGoogleGenerativeAI


from app.core.config import get_settings
from app.llm.base import LLMProvider




class GeminiProvider(LLMProvider):
    name = "gemini"


    def __init__(self, model: str | None = None, api_key: str | None = None) -> None:
        settings = get_settings()
        self._model = model or settings.gemini_model
        self._api_key = api_key or settings.gemini_api_key
        if not self._api_key:
            raise ValueError("GEMINI_API_KEY is required for the gemini provider")


    def chat_model(self) -> ChatGoogleGenerativeAI:
        return ChatGoogleGenerativeAI(
            model=self._model,
            google_api_key=self._api_key,  # type: ignore[arg-type]
            temperature=0.1,
        )
