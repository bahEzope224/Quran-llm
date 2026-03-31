from openai import OpenAI
from app.config import settings
from app.services.llm.prompt import SYSTEM_PROMPT

client = OpenAI(api_key=settings.openai_api_key)


def generate(prompt: str) -> str:
    response = client.chat.completions.create(
        model=settings.cloud_llm_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=settings.llm_temperature,
    )

    return response.choices[0].message.content.strip()