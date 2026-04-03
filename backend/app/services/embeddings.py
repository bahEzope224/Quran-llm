import json
import math
from urllib import error, request

from app.config import settings


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """Genere des embeddings via Ollama par batch (tronque a 512 chars)."""
    batch_size = 5
    all_embeddings = []

    for i in range(0, len(texts), batch_size):
        # On tronque chaque texte pour eviter de depasser la limite d'Ollama/all-minilm
        batch = [t[:512] for t in texts[i : i + batch_size]]
        
        if settings.embeddings_provider == "ollama":
            payload = {
                "model": settings.embeddings_model,
                "input": batch,
            }
            auth_header = {}
        else:
            # Format OpenAI/Cloud compatible
            payload = {
                "model": settings.embeddings_model,
                "input": batch,
            }
            auth_header = {"Authorization": f"Bearer {settings.llm_api_key}"} if settings.llm_api_key else {}

        http_request = request.Request(
            settings.embeddings_base_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", **auth_header},
            method="POST",
        )

        try:
            with request.urlopen(
                http_request,
                timeout=settings.llm_timeout_seconds,
            ) as response:
                response_payload = json.loads(response.read().decode("utf-8"))
                batch_embeddings = response_payload.get("embeddings", [])
                if isinstance(batch_embeddings, list):
                    all_embeddings.extend(batch_embeddings)
        except (error.URLError, error.HTTPError, TimeoutError, json.JSONDecodeError) as e:
            error_body = ""
            if hasattr(e, 'read'):
                try: error_body = e.read().decode("utf-8")
                except: pass
            print(f"ERROR in generate_embeddings batch {i}: {str(e)} | Body: {error_body}")
            continue

    return [
        [float(value) for value in embedding]
        for embedding in all_embeddings
        if isinstance(embedding, list)
    ]


def cosine_similarity(vector_a: list[float], vector_b: list[float]) -> float:
    """
    Calcule la similarite cosinus entre deux vecteurs.
    """
    if not vector_a or not vector_b or len(vector_a) != len(vector_b):
        return -1.0

    dot_product = sum(a * b for a, b in zip(vector_a, vector_b))
    norm_a = math.sqrt(sum(value * value for value in vector_a))
    norm_b = math.sqrt(sum(value * value for value in vector_b))
    if not norm_a or not norm_b:
        return -1.0

    return dot_product / (norm_a * norm_b)
