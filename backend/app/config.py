import os

from pydantic import BaseModel, Field


class Settings(BaseModel):
    app_name: str = "ILM AI"
    app_version: str = "0.16.2"
    app_description: str = "Backend FastAPI pour l'application ILM AI."
    frontend_origins: list[str] = Field(
        default_factory=lambda: os.getenv(
            "FRONTEND_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173,https://quran-llm.vercel.app",
        ).split(",")
    )
    default_language: str = "fr"
    default_mode: str = "clair"
    llm_provider: str = Field(
        default_factory=lambda: os.getenv("LLM_PROVIDER", "ollama")
    )
    llm_api_key: str | None = Field(default_factory=lambda: os.getenv("LLM_API_KEY"))
    llm_base_url: str = Field(
        default_factory=lambda: os.getenv(
            "LLM_BASE_URL",
            "http://127.0.0.1:11434/api/chat",
        )
    )
    llm_model: str = Field(
        default_factory=lambda: os.getenv("LLM_MODEL", "qwen2.5-coder:7b")
    )
    llm_translation_model: str = Field(
        default_factory=lambda: os.getenv("LLM_TRANSLATION_MODEL", "llama3.2:1b")
    )
    llm_timeout_seconds: float = Field(
        default_factory=lambda: float(os.getenv("LLM_TIMEOUT_SECONDS", "60"))
    )
    llm_temperature: float = Field(
        default_factory=lambda: float(os.getenv("LLM_TEMPERATURE", "0.2"))
    )
    embeddings_provider: str = Field(
        default_factory=lambda: os.getenv("EMBEDDINGS_PROVIDER", "ollama")
    )
    embeddings_model: str = Field(
        default_factory=lambda: os.getenv("EMBEDDINGS_MODEL", "all-minilm:latest")
    )
    embeddings_base_url: str = Field(
        default_factory=lambda: os.getenv(
            "EMBEDDINGS_BASE_URL",
            "http://127.0.0.1:11434/api/embed",
        )
    )
    embeddings_candidate_pool: int = Field(
        default_factory=lambda: int(os.getenv("EMBEDDINGS_CANDIDATE_POOL", "18"))
    )
    embeddings_batch_size: int = Field(
        default_factory=lambda: int(os.getenv("EMBEDDINGS_BATCH_SIZE", "5"))
    )
    embeddings_fallback_model: str = Field(
        default_factory=lambda: os.getenv("EMBEDDINGS_FALLBACK_MODEL", "BAAI/bge-small-en-v1.5")
    )
    embeddings_cache_path: str = Field(
        default_factory=lambda: os.getenv("EMBEDDINGS_CACHE_PATH", "backend/data/embedding_cache.json")
    )
    embeddings_retry_delay_seconds: float = Field(
        default_factory=lambda: float(os.getenv("EMBEDDINGS_RETRY_DELAY_SECONDS", "60"))
    )
    embeddings_spare_base_url: str | None = Field(
        default_factory=lambda: os.getenv("EMBEDDINGS_SPARE_BASE_URL", "") or None
    )


settings = Settings()
