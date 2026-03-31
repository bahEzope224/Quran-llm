from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "ILM Quran API"
    app_version: str = "0.1.0"
    app_description: str = "Backend FastAPI pour l'application ILM Quran."
    frontend_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    default_language: str = "fr"
    default_mode: str = "clair"


settings = Settings()

