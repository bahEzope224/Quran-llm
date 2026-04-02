import json
import re
from urllib import error, request

from app.config import settings


def _fallback_answer(context_chunks: list[dict[str, str]]) -> str:
    if not context_chunks:
        return (
            "Désolé, je n'ai pas trouvé de preuves spécifiques dans mes sources pour "
            "répondre avec certitude. Veuillez reformuler ou consulter un savant."
        )

    intro = (
        "Je n'ai pas pu générer une synthèse naturelle pour le moment, mais voici "
        "les textes bruts trouvés dans nos sources de référence :\n"
    )
    evidence_lines = [
        f"• {chunk['source']} ({chunk['ref']}) : {chunk['content']}"
        for chunk in context_chunks
    ]
    outro = (
        "\nNote : Une erreur technique a empêché la synthèse. Ces sources sont citées à titre indicatif."
    )
    return "\n".join([intro, *evidence_lines, outro])


def _extract_content(payload: dict[str, object]) -> str | None:
    if settings.llm_provider == "ollama":
        message = payload.get("message")
        if not isinstance(message, dict):
            return None
        content = message.get("content")
        return content.strip() if isinstance(content, str) else None

    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        return None

    first_choice = choices[0]
    if not isinstance(first_choice, dict):
        return None

    message = first_choice.get("message")
    if not isinstance(message, dict):
        return None

    content = message.get("content")
    return content.strip() if isinstance(content, str) else None


def _post_chat(messages: list[dict[str, str]], temperature: float | None = None, model: str | None = None) -> str | None:
    if settings.llm_provider != "ollama" and not settings.llm_api_key:
        return None

    target_temp = temperature if temperature is not None else settings.llm_temperature
    target_model = model if model is not None else settings.llm_model

    if settings.llm_provider == "ollama":
        payload = {
            "model": target_model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": target_temp,
            },
        }
        headers = {
            "Content-Type": "application/json", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }
    else:
        # Format OpenAI/Groq compatible
        payload = {
            "model": target_model,
            "temperature": target_temp,
            "messages": messages,
            "stream": False
        }
        headers = {
            "Content-Type": "application/json", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }
        if settings.llm_api_key:
            headers["Authorization"] = f"Bearer {settings.llm_api_key}"

    http_request = request.Request(
        settings.llm_base_url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    try:
        # On utilise le timeout specifique si fourni, sinon le global
        timeout = settings.llm_timeout_seconds
        with request.urlopen(
            http_request,
            timeout=timeout,
        ) as response:
            response_payload = json.loads(response.read().decode("utf-8"))
    except (error.URLError, error.HTTPError, TimeoutError, json.JSONDecodeError) as e:
        print(f"DEBUG: LLM API Error: {e}")
        return None

    return _extract_content(response_payload)


def _generate(prompt: str, model: str = settings.llm_translation_model, options: dict | None = None) -> str | None:
    """Appel bas niveau a /api/generate (format completion brut)."""
    url = settings.llm_base_url.replace("/chat", "/generate")
    # Options par defaut pour la traduction (tres strict)
    default_options = {"temperature": 0.0, "stop": ["\n", "."]}
    if options:
        default_options.update(options)
    elif "biographe" in prompt.lower() or "identification" in prompt.lower():
        # Moins restrictif pour les biographies
        default_options = {"temperature": 0.3}

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "raw": True,
        "options": default_options
    }
    http_request = request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(http_request, timeout=settings.llm_timeout_seconds) as response:
            resp = json.loads(response.read().decode("utf-8"))
            return resp.get("response", "").strip()
    except:
        return None


def _contains_arabic(text: str) -> bool:
    return bool(re.search(r"[\u0600-\u06FF]", text))


def _looks_english(text: str) -> bool:
    """Detecte si le texte est en anglais de maniere sensible aux sources islamiques."""
    if not text:
        return False
        
    # On cherche des mots typiques plus courts
    ascii_words = re.findall(r"\b[a-zA-Z]{2,}\b", text)
    if len(ascii_words) < 3:
        return False

    common_english_markers = {
        "the", "and", "with", "that", "this", "from", "they", "their", "were", 
        "allah", "prophet", "narrated", "messenger", "book", "chapter", 
        "verse", "means", "said", "according", "follows", "translation",
        "commentary", "report", "Sahih", "Bukhari", "Muslim", "Tirmidhi"
    }
    
    words_lower = {word.lower() for word in ascii_words}
    intersection = common_english_markers.intersection(words_lower)
    
    # Si on trouve UN de ces mots marqueurs ou si on a assez de mots ASCII
    return len(intersection) >= 1 or len(words_lower) > 6


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
    """Nettoie le texte traduit des prefixes ou notes d'IA parasites."""
    if not text:
        return ""
    cleaned = text.strip()
    noisy_patterns = [
        r"^je suis un traducteur.*",
        r"^voici la traduction.*:",
        r"^traduction\s*:.*",
        r"^en français\s*:.*",
        r"^ceci est une traduction.*",
        r"\(Note\s*:.*\)",
        r"^Note\s*:.*",
        r"^Assistant\s*:.*",
    ]
    for pattern in noisy_patterns:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE | re.MULTILINE).strip()
    
    # Nettoyage final des guillemets et espaces
    cleaned = cleaned.strip('" ').strip("' ").strip()
    return cleaned


def generate_answer(prompt: str, context_chunks: list[dict], options: dict | None = None) -> dict:
    """Genere une reponse finale a partir d'un prompt et de contextes."""
    # Par defaut, on garde un peu de structure
    default_options = {"temperature": 0.3, "stop": ["\n\n", "User:", "Assistant:"]}
    if options:
        default_options.update(options)

    messages = [
        {
            "role": "system",
            "content": (
                "Tu es un assistant islamique francophone extrêmement rigoureux et fidèle aux textes. "
                "Tu réponds EXCLUSIVEMENT à partir du contexte fourni, sans rien inventer d'extérieur. "
                "\n\nRÈGLES CRITIQUES D'INTERPRÉTATION :\n"
                "1. RESTE STRICTEMENT SUR LE SUJET : Si on te pose une question sur le JEÛNE, ne réponds pas sur la PATIENCE ou un autre thème connexe.\n"
                "2. PRÉCISION DOCTRINALE : Ne transforme JAMAIS un raisonnement conditionnel en affirmation (ex: 'Si... alors' n'est pas 'Il faut...').\n"
                "3. FRÉQUENCES : Sois exact sur les obligations (ex: Hajj = UNE SEULE FOIS dans la vie si capable).\n"
                "4. TRADUCTION DE HAUTE QUALITÉ : Traduis fidèlement les sources anglaises en français soigné, en respectant le sens théologique.\n"
                "5. TEXTES ARABES : Recopie l'arabe à l'identique, sans JAMAIS le modifier.\n"
                "6. NOM DU PROPHÈTE : N'utilise JAMAIS le nom 'Mahomet'. Utilise TOUJOURS 'Muhammad PBSL' (Paix et Bénédiction de Dieu sur Lui)."
            ),
        },
        {
            "role": "user",
            "content": prompt,
        },
    ]
    answer = _post_chat(messages, temperature=default_options.get("temperature"))
    if not answer:
        return {"answer": _fallback_answer(context_chunks)}

    return {"answer": answer, "sources": context_chunks}


def translate_text_to_french(text: str, force: bool = False) -> str:
    """Traduit un texte anglais en francais de maniere brute et technique."""
    if not text:
        return text
        
    # Si on ne force pas, on verifie si c'est de l'anglais
    if not force and not _looks_english(text):
        return text

    source_text = _shorten_text(text)
    print(f"DEBUG: [TRANS] Tentative de traduction ({len(source_text)} chars)...")

    prompt = (
        "Translate to French. ONLY output the translation. NO notes. NO preamble. NO context.\n"
        "Example Input: Is it forbidden?\n"
        "Example Output: Est-ce interdit?\n\n"
        f"Translate: {source_text}"
    )

    # Utiliser le modele de traduction dedie (plus leger/rapide)
    translated = _post_chat(
        [{"role": "user", "content": prompt}],
        temperature=0.0,
        model=settings.llm_translation_model
    )
    
    if translated:
        clean_text = _clean_translated_text(translated)
        print(f"DEBUG: [TRANS] Succès.")
        return clean_text
    else:
        print(f"DEBUG: [TRANS] Échec ou Timeout. Retour au texte original.")
        return source_text


def translate_french_to_english(text: str) -> str:
    """Traduit une question FR en EN de maniere tres robuste par completion brute."""
    if not text:
        return text

    # Prompt mono-shot de completion pure (format raw d'Ollama)
    prompt = (
        "Translate French to English.\n"
        "FR: 'Quels sont les piliers ?'\n"
        "EN: 'what are the pillars of islam?'\n"
        f"FR: '{text}'\n"
        "EN: '"
    )

    translated = _generate(prompt)
    
    if not translated:
        # Fallback sur la Keyword Map déjà implémentée dans rag_pipeline.py
        return text
        
    return translated.strip().strip("'").strip('"').lower()
