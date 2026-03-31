import os
from pydantic import BaseModel, Field


class Settings(BaseModel):
    # App
    app_name: str = "ILM Quran API"
    app_version: str = "0.1.0"
    app_description: str = "Backend FastAPI pour l'application ILM Quran."

    # Frontend
    frontend_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # User defaults
    default_language: str = "fr"
    default_mode: str = "clair"

    # 🔀 MODE HYBRID
    llm_mode: str = Field(default_factory=lambda: os.getenv("LLM_MODE", "hybrid"))
    # options: "local", "cloud", "hybrid"

    # 🧠 LOCAL LLM (Ollama)
    local_llm_model: str = Field(
        default_factory=lambda: os.getenv("LOCAL_LLM_MODEL", "mistral")
    )
    local_llm_base_url: str = Field(
        default_factory=lambda: os.getenv(
            "LOCAL_LLM_BASE_URL",
            "http://127.0.0.1:11434/api/generate",
        )
    )

    # ☁️ CLOUD LLM (OpenAI)
    openai_api_key: str | None = Field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY")
    )
    cloud_llm_model: str = Field(
        default_factory=lambda: os.getenv("CLOUD_LLM_MODEL", "gpt-4.1")
    )

    # ⚙️ Paramètres communs
    llm_timeout_seconds: float = Field(
        default_factory=lambda: float(os.getenv("LLM_TIMEOUT_SECONDS", "30"))
    )
    llm_temperature: float = Field(
        default_factory=lambda: float(os.getenv("LLM_TEMPERATURE", "0.2"))
    )

    # 📊 Embeddings
    embeddings_provider: str = Field(
        default_factory=lambda: os.getenv("EMBEDDINGS_PROVIDER", "ollama")
    )
    embeddings_model: str = Field(
        default_factory=lambda: os.getenv("EMBEDDINGS_MODEL", "all-minilm")
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


settings = Settings()