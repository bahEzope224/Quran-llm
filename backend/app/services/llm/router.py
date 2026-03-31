from app.config import settings


def route(question: str) -> str:
    # mode forcé
    if settings.llm_mode == "local":
        return "local"
    if settings.llm_mode == "cloud":
        return "cloud"

    # mode hybrid
    question = question.lower()

    if len(question) > 150 or any(
        w in question
        for w in ["pourquoi", "explique", "différence", "raison", "comment"]
    ):
        return "cloud"

    return "local"