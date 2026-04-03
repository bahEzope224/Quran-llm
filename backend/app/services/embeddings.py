import json
import math
from urllib import error, request

from app.config import settings
from app.core.exceptions import LLMException


# Cache global pour le moteur de secours (FastEmbed)
_LOCAL_EMBEDDER = None


def _get_local_embedder():
    """Charge dynamiquement FastEmbed pour economiser la RAM si non utilise."""
    global _LOCAL_EMBEDDER
    if _LOCAL_EMBEDDER is None:
        try:
            from fastembed import TextEmbedding
            print("DEBUG: Loading Local FastEmbed (all-MiniLM-L6-v2)...")
            _LOCAL_EMBEDDER = TextEmbedding(model_name="BAAI/bge-small-en-v1.5") # Tres rapide et leger
        except Exception as e:
            print(f"CRITICAL: Impossible de charger FastEmbed: {e}")
            raise
    return _LOCAL_EMBEDDER


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """Genere des embeddings via Ollama ou Fallback Local (FastEmbed)."""
    batch_size = 5
    all_embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = [t[:512] for t in texts[i : i + batch_size]]
        
        # 1. TENTATIVE VIA API (Ollama ou Cloud)
        use_fallback = False
        try:
            if settings.embeddings_provider == "ollama":
                payload = {"model": settings.embeddings_model, "input": batch}
                auth_header = {}
            else:
                payload = {"model": settings.embeddings_model, "input": batch}
                auth_header = {"Authorization": f"Bearer {settings.llm_api_key}"} if settings.llm_api_key else {}

            http_request = request.Request(
                settings.embeddings_base_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json", "User-Agent": "ILM-AI-Backend", **auth_header},
                method="POST",
            )

            with request.urlopen(http_request, timeout=settings.llm_timeout_seconds) as response:
                response_payload = json.loads(response.read().decode("utf-8"))
                batch_embeddings = response_payload.get("embeddings", [])
                if isinstance(batch_embeddings, list) and batch_embeddings:
                    all_embeddings.extend(batch_embeddings)
                    continue # Succès, on passe au batch suivant
                else:
                    use_fallback = True

        except (error.URLError, error.HTTPError, TimeoutError, ConnectionRefusedError):
            # Si on est sur localhost et que ca echoue, c'est normal en PROD
            if "127.0.0.1" in settings.embeddings_base_url or "localhost" in settings.embeddings_base_url:
                print(f"DEBUG: Ollama local non detecte au Batch {i}. Basculement sur FastEmbed.")
                use_fallback = True
            else:
                raise
        except Exception as e:
            print(f"ERROR: Erreur imprevue au Batch {i}: {e}")
            use_fallback = True

        # 2. BASCULEMENT SUR FASTEMBED (Local CPU)
        if use_fallback:
            try:
                model = _get_local_embedder()
                # FastEmbed renvoie un iterateur de numpy arrays
                batch_res = list(model.embed(batch))
                all_embeddings.extend([list(map(float, emb)) for emb in batch_res])
            except Exception as fe_err:
                raise LLMException(
                    message=f"Echec total de la generation (Batch {i}). Fallback local echoue.",
                    location="embeddings_service.generate_embeddings",
                    details={"ollama_fail": "inaccessible", "fastembed_err": str(fe_err)}
                )

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
