import json
import re
from urllib import error, request
from app.config import settings


def _fallback_answer(context_chunks: list[dict[str, str]]) -> str:
    if not context_chunks:
        return (
            "Je n'ai pas trouve de preuves pertinentes dans les donnees locales pour "
            "repondre de maniere fiable."
        )

    intro = (
        "Voici une synthese fondee sur les sources retrouvees dans la base locale."
    )
    evidence_lines = [
        f"{index}. {chunk['source']} ({chunk['ref']}) : {chunk['content']}"
        for index, chunk in enumerate(context_chunks, start=1)
    ]
    outro = (
        "Si vous configurez une cle API LLM, la reponse sera reformulee de maniere plus naturelle."
    )
    return "\n".join([intro, *evidence_lines, outro])


def _extract_content(payload: dict[str, object]) -> str | None:
    """Extrait le texte de la réponse selon le format de l'API (OpenAI ou local)."""
    # Pour OpenAI style chat completions
    choices = payload.get("choices")
    if choices and isinstance(choices, list) and len(choices) > 0:
        first_choice = choices[0]
        if isinstance(first_choice, dict):
            message = first_choice.get("message")
            if isinstance(message, dict):
                content = message.get("content")
                return content.strip() if isinstance(content, str) else None

    # Pour un format simple local LLM
    content = payload.get("content")
    if isinstance(content, str):
        return content.strip()

    return None


def _post_chat(messages: list[dict[str, str]]) -> str | None:
    """Envoie les messages à un LLM local ou cloud selon settings."""
    use_local = settings.llm_mode in ("local", "hybrid")
    use_cloud = settings.llm_mode in ("cloud", "hybrid") and settings.openai_api_key

    if not use_local and not use_cloud:
        return None

    # Priorité: local si activé
    if use_local:
        payload = {
            "model": settings.local_llm_model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": settings.llm_temperature},
        }
        headers = {"Content-Type": "application/json"}
        url = settings.local_llm_base_url
    else:
        payload = {
            "model": settings.cloud_llm_model,
            "temperature": settings.llm_temperature,
            "messages": messages,
        }
        headers = {
            "Authorization": f"Bearer {settings.openai_api_key}",
            "Content-Type": "application/json",
        }
        url = "https://api.openai.com/v1/chat/completions"

    http_request = request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    try:
        with request.urlopen(http_request, timeout=settings.llm_timeout_seconds) as response:
            response_payload = json.loads(response.read().decode("utf-8"))
    except (error.URLError, error.HTTPError, TimeoutError, json.JSONDecodeError):
        return None

    return _extract_content(response_payload)


def _contains_arabic(text: str) -> bool:
    return bool(re.search(r"[\u0600-\u06FF]", text))


def _looks_english(text: str) -> bool:
    ascii_words = re.findall(r"\b[a-zA-Z]{3,}\b", text)
    if len(ascii_words) < 4:
        return False

    common_english_markers = {
        "the",
        "and",
        "with",
        "that",
        "this",
        "from",
        "they",
        "their",
        "were",
        "allah",
    }
    return len(common_english_markers.intersection({word.lower() for word in ascii_words})) >= 2


def _shorten_text(text: str, max_chars: int = 500) -> str:
    compact = " ".join(text.split())
    if len(compact) <= max_chars:
        return compact

    shortened = compact[:max_chars]
    last_stop = max(shortened.rfind(". "), shortened.rfind("; "), shortened.rfind(", "))
    if last_stop > max_chars // 2:
        shortened = shortened[: last_stop + 1]
    return shortened.strip()


def _clean_translated_text(text: str) -> str:
    cleaned = text.strip()
    noisy_prefixes = (
        "je suis un traducteur",
        "le passage anglais est",
        "traduction :",
        "voici la traduction",
    )
    lower_cleaned = cleaned.lower()
    if any(lower_cleaned.startswith(prefix) for prefix in noisy_prefixes):
        markers = ['\n\n', ':\n', '"\n']
        for marker in markers:
            if marker in cleaned:
                cleaned = cleaned.split(marker, 1)[-1].strip()
                break
    return cleaned.strip('" ').strip()


def generate_answer(prompt: str, context_chunks: list[dict[str, str]]) -> dict[str, object]:
    """Genere une reponse via LLM local ou cloud selon settings."""
    use_local = settings.llm_mode in ("local", "hybrid")
    use_cloud = settings.llm_mode in ("cloud", "hybrid") and settings.openai_api_key

    if not use_local and not use_cloud:
        return {"answer": _fallback_answer(context_chunks)}

    messages = [
        {
            "role": "system",
            "content": (
                "Tu es un assistant islamique francophone. "
                "Tu reponds uniquement a partir du contexte fourni. "
                "Si une information n'est pas dans le contexte, dis-le clairement. "
                "Ne fabrique ni verset, ni hadith, ni reference. "
                "Traduis en francais les passages anglais que tu cites. "
                "Si tu recopies un passage arabe, recopie-le exactement, sans le modifier."
            ),
        },
        {"role": "user", "content": prompt},
    ]

    answer = _post_chat(messages)
    if not answer:
        return {"answer": _fallback_answer(context_chunks)}

    return {"answer": answer}


def translate_text_to_french(text: str) -> str:
    """Traduit un texte anglais en francais tout en laissant l'arabe intact."""
    if not text or not _looks_english(text):
        return text

    source_text = _shorten_text(text)

    translated = _post_chat(
        [
            {
                "role": "system",
                "content": (
                    "Tu es un traducteur precis. "
                    "Traduis ce passage anglais en francais. "
                    "Ne resumer pas. "
                    "Ne commente pas. "
                    "Retourne uniquement la traduction finale. "
                    "Garde les noms propres, references et expressions arabes tels quels. "
                    "Si une portion est en arabe, recopie-la exactement sans alteration."
                ),
            },
            {"role": "user", "content": source_text},
        ]
    )

    return _clean_translated_text(translated) if translated else source_text