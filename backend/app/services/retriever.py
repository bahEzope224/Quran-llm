from app.services.embeddings import generate_embeddings
from app.db.vector_store import search_similar_chunks


def retrieve_relevant_chunks(query: str, top_k: int = 3) -> list[dict[str, str]]:
    """Cree un embedding de la question puis recupere les chunks pertinents."""
    embedding = generate_embeddings([query])[0]
    return search_similar_chunks(query=query, embedding=embedding, top_k=top_k)
