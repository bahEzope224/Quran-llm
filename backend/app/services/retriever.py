from app.config import settings
from app.services.embeddings import cosine_similarity, generate_embeddings
from app.db.vector_store import search_similar_chunks


def retrieve_relevant_chunks(query: str, top_k: int = 3) -> list[dict[str, str]]:
    """Preselction lexicale puis reranking semantique via embeddings locaux."""
    candidate_pool = max(top_k, settings.embeddings_candidate_pool)
    candidates = search_similar_chunks(query=query, embedding=None, top_k=candidate_pool)
    if not candidates:
        return []

    texts = [query, *[chunk["content"] for chunk in candidates]]
    embeddings = generate_embeddings(texts)
    if len(embeddings) != len(texts):
        return candidates[:top_k]

    query_embedding = embeddings[0]
    ranked_candidates = []
    for chunk, chunk_embedding in zip(candidates, embeddings[1:]):
        lexical_score = float(chunk.get("lexical_score", 0))
        type_boost = 3.0 if chunk["type"] == "quran" else 1.5 if chunk["type"] == "hadith" else 1.0
        semantic_score = cosine_similarity(query_embedding, chunk_embedding)
        ranked_candidates.append(
            (
                (semantic_score * 10) + lexical_score + type_boost,
                chunk,
            )
        )

    ranked_candidates.sort(key=lambda item: item[0], reverse=True)
    return [chunk for _, chunk in ranked_candidates[:top_k]]
