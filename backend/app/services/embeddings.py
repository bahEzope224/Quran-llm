import hashlib
import json
import math
import time
from pathlib import Path
from urllib import error, request

from app.config import settings
from app.core.exceptions import LLMException


# Cache global pour le moteur de secours (FastEmbed)
_LOCAL_EMBEDDER = None
_EMBEDDING_CACHE: dict[str, list[float]] | None = None


def _get_local_embedder():
    """Charge dynamiquement FastEmbed pour economiser la RAM si non utilise."""
    global _LOCAL_EMBEDDER
    if _LOCAL_EMBEDDER is None:
        try:
            from fastembed import TextEmbedding
            print(f"DEBUG: Loading Local FastEmbed ({settings.embeddings_fallback_model})...")
            _LOCAL_EMBEDDER = TextEmbedding(model_name=settings.embeddings_fallback_model)
        except Exception as e:
            print(f"CRITICAL: Impossible de charger FastEmbed: {e}")
            raise
    return _LOCAL_EMBEDDER


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _load_embedding_cache() -> dict[str, list[float]]:
    global _EMBEDDING_CACHE
    if _EMBEDDING_CACHE is None:
        cache_path = Path(settings.embeddings_cache_path)
        if cache_path.is_file():
            try:
                _EMBEDDING_CACHE = json.loads(cache_path.read_text())
            except json.JSONDecodeError:
                _EMBEDDING_CACHE = {}
        else:
            _EMBEDDING_CACHE = {}
    return _EMBEDDING_CACHE


def _persist_embedding_cache(cache: dict[str, list[float]]) -> None:
    cache_path = Path(settings.embeddings_cache_path)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(cache))


def _build_request(base_url: str, batch: list[str]) -> request.Request:
    payload = {"model": settings.embeddings_model, "input": batch}
    auth_header = (
        {}
        if settings.embeddings_provider == "ollama"
        else {"Authorization": f"Bearer {settings.llm_api_key}"} if settings.llm_api_key else {}
    )
    return request.Request(
        base_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "ILM-AI-Backend", **auth_header},
        method="POST",
    )


def _call_embedding_provider(
    batch: list[str],
    batch_idx: int,
    base_url: str | None = None,
    used_spare: bool = False,
) -> tuple[list[list[float]], float]:
    base_url = base_url or settings.embeddings_base_url
    start = time.perf_counter()
    try:
        http_request = _build_request(base_url, batch)
        with request.urlopen(http_request, timeout=settings.llm_timeout_seconds) as response:
            response_payload = json.loads(response.read().decode("utf-8"))
            batch_embeddings = response_payload.get("embeddings", [])
            status_code = getattr(response, "status", response.getcode())
            duration = time.perf_counter() - start
            if isinstance(batch_embeddings, list) and batch_embeddings:
                print(
                    f"DEBUG: Provider embeddings batch {batch_idx} succeeded in {duration:.2f}s (code {status_code}, size {len(batch)})."
                )
                return [list(map(float, emb)) for emb in batch_embeddings], duration
            print(
                f"DEBUG: Provider batch {batch_idx} returned empty payload (status {status_code})."
            )
            raise error.HTTPError(base_url, status_code, "Empty payload", hdrs=None, fp=None)
    except error.HTTPError as http_err:
        if (
            http_err.code == 404
            and settings.embeddings_spare_base_url
            and not used_spare
        ):
            if settings.embeddings_retry_delay_seconds > 0:
                time.sleep(settings.embeddings_retry_delay_seconds)
            print(
                f"DEBUG: Primary embeddings URL returned 404; retrying batch {batch_idx} against spare endpoint."
            )
            return _call_embedding_provider(
                batch,
                batch_idx,
                base_url=settings.embeddings_spare_base_url,
                used_spare=True,
            )
        print(
            f"DEBUG: Provider HTTP error batch {batch_idx} ({http_err}). Switching to FastEmbed fallback."
        )
        return _run_fastembed(batch, batch_idx)
    except (error.URLError, TimeoutError, ConnectionRefusedError) as exc:
        print(
            f"DEBUG: Provider failure batch {batch_idx} ({exc}). Switching to FastEmbed fallback."
        )
        return _run_fastembed(batch, batch_idx)
    except Exception as exc:
        print(f"ERROR: Unexpected provider failure batch {batch_idx}: {exc}. Using fallback.")
        return _run_fastembed(batch, batch_idx)


def _run_fastembed(batch: list[str], batch_idx: int) -> tuple[list[list[float]], float]:
    fallback_start = time.perf_counter()
    try:
        model = _get_local_embedder()
        batch_res = list(model.embed(batch))
        duration = time.perf_counter() - fallback_start
        print(f"DEBUG: FastEmbed batch {batch_idx} done in {duration:.2f}s.")
        return [list(map(float, emb)) for emb in batch_res], duration
    except Exception as fe_err:
        raise LLMException(
            message=f"Echec total de la generation (batch {batch_idx}). Fallback local echoue.",
            location="embeddings_service.generate_embeddings",
            details={"fastembed_err": str(fe_err)}
        )


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """Genere des embeddings pour les textes en combinant API et cache local."""
    batch_size = max(1, settings.embeddings_batch_size)
    if not texts:
        return []
    truncated_texts = [text[:512] for text in texts]
    cache = _load_embedding_cache()
    embeddings: list[list[float] | None] = [None] * len(truncated_texts)
    pending_indices: list[int] = []

    for idx, text in enumerate(truncated_texts):
        if idx == 0:
            pending_indices.append(idx)
            continue

        cache_key = _hash_text(text)
        cached = cache.get(cache_key)
        if cached:
            embeddings[idx] = [float(value) for value in cached]
        else:
            pending_indices.append(idx)

    if 0 not in pending_indices:
        pending_indices.insert(0, 0)

    cache_updated = False
    for offset in range(0, len(pending_indices), batch_size):
        batch_indices = pending_indices[offset : offset + batch_size]
        batch_texts = [truncated_texts[idx] for idx in batch_indices]
        batch_embeddings, duration = _call_embedding_provider(batch_texts, offset)
        if duration > settings.llm_timeout_seconds:
            print(
                f"WARNING: Embedding batch {offset} took {duration:.1f}s, nearing timeout ({settings.llm_timeout_seconds}s)."
            )

        for idx, embedding in zip(batch_indices, batch_embeddings):
            normalized = [float(value) for value in embedding]
            embeddings[idx] = normalized
            if idx != 0:
                cache_key = _hash_text(truncated_texts[idx])
                cache[cache_key] = normalized
                cache_updated = True

    if cache_updated:
        _persist_embedding_cache(cache)

    if any(embed is None for embed in embeddings):
        raise LLMException(
            message="Embedding generation incomplete.",
            location="embeddings_service.generate_embeddings",
            details={"texts": len(texts), "filled": sum(1 for embed in embeddings if embed is not None)},
        )

    return [embed for embed in embeddings if embed is not None]


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
