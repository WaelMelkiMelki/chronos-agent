"""Application settings loaded from environment variables."""


from functools import lru_cache
from typing import Literal


from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict




class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


    # ─── App ────────────────────────────────────
    app_name: str = "chronos-agent"
    app_env: Literal["development", "staging", "production"] = "development"
    app_secret_key: str = Field(..., min_length=32)
    app_log_level: str = "INFO"
    app_base_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:3000"


    # ─── Database ───────────────────────────────
    database_url: str


    # ─── JWT ────────────────────────────────────
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    jwt_refresh_token_expire_days: int = 7


    # ─── Crypto ─────────────────────────────────
    fernet_key: str


    # ─── Google OAuth ───────────────────────────
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/api/v1/auth/google/callback"
    google_scopes: str = "https://www.googleapis.com/auth/calendar"


    # ─── LLM ────────────────────────────────────
    llm_provider: Literal["ollama", "groq", "gemini", "openai-compatible"] = "ollama"
    llm_model: str = "qwen3:4b"


    ollama_base_url: str = "http://ollama:11434"


    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"


    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"


    # ─── Feature flags ──────────────────────────
    feature_qdrant: bool = False
    feature_mcp: bool = False
    qdrant_url: str = "http://qdrant:6333"


    @field_validator("app_secret_key")
    @classmethod
    def _secret_not_placeholder(cls, v: str) -> str:
        if v.startswith("change-me"):
            raise ValueError("APP_SECRET_KEY must be changed from placeholder")
        return v




@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
