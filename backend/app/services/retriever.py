from app.config import settings
from app.services.embeddings import cosine_similarity, generate_embeddings
from app.db.vector_store import search_similar_chunks


def retrieve_relevant_chunks(query: str, top_k: int = 5, topic: str | None = None) -> list[dict[str, str]]:
    """Preselction lexicale puis reranking semantique via embeddings locaux."""
    candidate_pool = max(top_k * 3, settings.embeddings_candidate_pool)
    candidates = search_similar_chunks(query=query, embedding=None, top_k=candidate_pool)
    if not candidates:
        return []

    texts = [query, *[chunk["content"] for chunk in candidates]]
    embeddings = generate_embeddings(texts)
    
    print(f"DEBUG: Texts: {len(texts)} | Embeddings: {len(embeddings)} | Topic: {topic}")
    
    if len(embeddings) != len(texts):
        print(f"WARNING: Embedding count mismatch! Using lexical fallback. (Texts: {len(texts)}, Embeds: {len(embeddings)})")
        for chunk in candidates:
            chunk["semantic_score"] = 0.6
        return candidates[:top_k]

    query_embedding = embeddings[0]
    ranked_candidates = []
    for chunk, chunk_embedding in zip(candidates, embeddings[1:]):
        lexical_score = float(chunk.get("lexical_score", 0))
        semantic_score = cosine_similarity(query_embedding, chunk_embedding)
        
        # Boost dynamique base sur le topic
        chunk_type = chunk.get("type", "unknown")
        if topic == "biography":
            # Si on cherche une info bio, la Seerah est ROI
            type_boost = 1.8 if chunk_type == "seerah" else 1.0 # Le Coran devient neutre
        else:
            # Boosts par defaut (priorite Coran/Sunnah pour la charia)
            type_boost = 1.5 if chunk_type == "quran" else 1.2 if chunk_type == "hadith" else 1.0
        
        # Formule de score equilibree : le semantique domine (x15)
        final_score = (float(semantic_score) * 15) + (lexical_score * 0.5) + type_boost
        
        chunk["semantic_score"] = float(semantic_score)
        chunk["final_score"] = float(final_score)
        
        ranked_candidates.append((final_score, chunk))

    ranked_candidates.sort(key=lambda item: item[0], reverse=True)
    return [chunk for _, chunk in ranked_candidates[:top_k]]


def retrieve_tafsir_by_ref(ref: str) -> dict[str, str] | None:
    """Recupere le Tafsir, suit les redirections (ex: '2:43' -> '2:42')."""
    from app.db.vector_store import load_ibn_kathir_tafsir_dataset, _strip_html, _get_tafsir_text, _infer_tags
    
    dataset = load_ibn_kathir_tafsir_dataset()
    original_ref = ref
    visited = {ref}
    
    current_key = ref
    while current_key in dataset:
        val = dataset[current_key]
        
        # Si la valeur est un dictionnaire, on a trouve le texte
        if isinstance(val, dict):
            text = _strip_html(_get_tafsir_text(val))
            if text:
                content = text[:2000]
                return {
                    "type": "tafsir",
                    "source": "Ibn Kathir via Qul/Tarteel",
                    "ref": f"Ibn Kathir {original_ref}",
                    "content": content,
                    "tags": _infer_tags(
                        ref=original_ref,
                        source="Ibn Kathir via Qul/Tarteel",
                        content=content,
                        source_type="tafsir",
                    ),
                }
            return None
        
        # Si c'est une chaine (redirection), on suit le lien
        if isinstance(val, str):
            if val in visited: # Protection boucle
                break
            visited.add(val)
            current_key = val
            continue
            
        break
        
    return None
def retrieve_specific_quran_verse(ref: str) -> dict[str, str] | None:
    """Récupère un verset spécifique par sa référence pour injection de sécurité."""
    from app.db.vector_store import get_verse_by_ref
    return get_verse_by_ref(ref)
