import json
import math
from urllib import error, request

from app.config import settings


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """Genere des embeddings via Ollama et retourne une liste vide en fallback."""
    if not texts:
        return []

    if settings.embeddings_provider != "ollama":
        return []

    payload = {
        "model": settings.embeddings_model,
        "input": texts,
    }
    http_request = request.Request(
        settings.embeddings_base_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with request.urlopen(
            http_request,
            timeout=settings.llm_timeout_seconds,
        ) as response:
            response_payload = json.loads(response.read().decode("utf-8"))
    except (error.URLError, error.HTTPError, TimeoutError, json.JSONDecodeError):
        return []

    embeddings = response_payload.get("embeddings")
    if not isinstance(embeddings, list):
        return []

    return [
        [float(value) for value in embedding]
        for embedding in embeddings
        if isinstance(embedding, list)
    ]


def cosine_similarity(vector_a: list[float], vector_b: list[float]) -> float:
    if not vector_a or not vector_b or len(vector_a) != len(vector_b):
        return -1.0

    dot_product = sum(a * b for a, b in zip(vector_a, vector_b))
    norm_a = math.sqrt(sum(value * value for value in vector_a))
    norm_b = math.sqrt(sum(value * value for value in vector_b))
    if not norm_a or not norm_b:
        return -1.0

    return dot_product / (norm_a * norm_b)
