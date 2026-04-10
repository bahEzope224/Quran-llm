import os
from pydantic import BaseModel, Field

def _get_env_robust(key: str, default: str) -> str:
    val = os.getenv(key)
    if not val or val.strip().lower() == "none":
        return default
    return val

class Settings(BaseModel):
    app_name: str = "ILM AI"
    app_version: str = "0.17.2"
    app_description: str = "Backend FastAPI pour l'application ILM AI."
    
    frontend_origins: list[str] = Field(
        default_factory=lambda: _get_env_robust(
            "FRONTEND_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173,https://quran-llm.vercel.app"
        ).split(",")
    )
    
    default_language: str = "fr"
    default_mode: str = "clair"
    
    llm_provider: str = Field(default_factory=lambda: _get_env_robust("LLM_PROVIDER", "openai"))
    llm_api_key: str | None = Field(default_factory=lambda: os.getenv("LLM_API_KEY") if os.getenv("LLM_API_KEY") and os.getenv("LLM_API_KEY").lower() != "none" else None)
    llm_base_url: str = Field(default_factory=lambda: _get_env_robust("LLM_BASE_URL", "https://api.openai.com/v1"))
    llm_model: str = Field(default_factory=lambda: _get_env_robust("LLM_MODEL", "gpt-4o-mini"))
    llm_translation_model: str = Field(default_factory=lambda: _get_env_robust("LLM_TRANSLATION_MODEL", "gpt-4o-mini"))
    
    llm_timeout_seconds: float = Field(default_factory=lambda: float(_get_env_robust("LLM_TIMEOUT_SECONDS", "60")))
    llm_temperature: float = Field(default_factory=lambda: float(_get_env_robust("LLM_TEMPERATURE", "0.2")))
    
    embeddings_provider: str = Field(default_factory=lambda: _get_env_robust("EMBEDDINGS_PROVIDER", "openai"))
    embeddings_model: str = Field(default_factory=lambda: _get_env_robust("EMBEDDINGS_MODEL", "text-embedding-3-small"))
    embeddings_base_url: str = Field(default_factory=lambda: _get_env_robust("EMBEDDINGS_BASE_URL", "https://api.openai.com/v1/embeddings"))

    
    embeddings_candidate_pool: int = Field(default_factory=lambda: int(os.getenv("EMBEDDINGS_CANDIDATE_POOL") or "18"))
    embeddings_batch_size: int = Field(default_factory=lambda: int(os.getenv("EMBEDDINGS_BATCH_SIZE") or "5"))
    embeddings_fallback_model: str = Field(default_factory=lambda: os.getenv("EMBEDDINGS_FALLBACK_MODEL") or "BAAI/bge-small-en-v1.5")
    embeddings_cache_path: str = Field(default_factory=lambda: os.getenv("EMBEDDINGS_CACHE_PATH") or "backend/data/embedding_cache.json")
    embeddings_retry_delay_seconds: float = Field(default_factory=lambda: float(os.getenv("EMBEDDINGS_RETRY_DELAY_SECONDS") or "60"))
    embeddings_spare_base_url: str | None = Field(default_factory=lambda: os.getenv("EMBEDDINGS_SPARE_BASE_URL") or None)

settings = Settings()
