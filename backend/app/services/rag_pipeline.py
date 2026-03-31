from app.models.schemas import ChatResponse, ChatRequest
from app.services.llm import generate_answer
from app.services.retriever import retrieve_relevant_chunks


def build_rag_prompt(payload: ChatRequest, chunks: list[dict[str, str]]) -> str:
    context_block = "\n".join(
        f"- [{chunk['type']}] {chunk['source']} ({chunk['ref']}): {chunk['content']}"
        for chunk in chunks
    )

    return (
        "Tu es un assistant islamique francophone.\n"
        "Reponds clairement en francais.\n"
        "Cite uniquement les preuves presentes dans le contexte.\n"
        f"Mode demande: {payload.mode}\n"
        f"Ecole juridique: {payload.profile.legal_school}\n"
        f"Langue preferee: {payload.profile.language}\n"
        f"Question: {payload.question}\n"
        "Contexte RAG:\n"
        f"{context_block}"
    )


def run_rag_pipeline(payload: ChatRequest) -> ChatResponse:
    """Pipeline RAG: retrieval, construction du prompt, generation."""
    chunks = retrieve_relevant_chunks(query=payload.question, top_k=3)
    prompt = build_rag_prompt(payload=payload, chunks=chunks)
    generated = generate_answer(prompt=prompt, context_chunks=chunks)

    return ChatResponse(
        answer=generated["answer"],
        sources=generated["sources"],
    )
