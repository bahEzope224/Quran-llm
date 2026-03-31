from app.config import settings
import requests
from app.services.llm.prompt import SYSTEM_PROMPT


def generate(prompt: str) -> str:
    full_prompt = SYSTEM_PROMPT + "\n\n" + prompt

    response = requests.post(
        settings.local_llm_base_url,
        json={
            "model": settings.local_llm_model,
            "prompt": full_prompt,
            "stream": False,
        },
        timeout=settings.llm_timeout_seconds,
    )

    return response.json()["response"].strip()