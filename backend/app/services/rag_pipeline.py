import re
import unicodedata

from app.models.schemas import ChatRequest, ChatResponse, SourceItem
from app.services.llm import generate_answer, translate_text_to_french
from app.services.retriever import retrieve_relevant_chunks

SOURCE_PRIORITY = ["quran", "hadith", "tafsir"]
QUESTION_TOPIC_MAP = {
    "prayer": ["priere", "prayer", "salat", "salah"],
    "fasting": ["jeune", "fast", "fasting", "siyam", "sawm", "ramadan"],
    "interest": ["interet", "interets", "interest", "usury", "riba"],
    "pillars": ["pilier", "piliers", "pillar", "pillars", "cinq piliers", "five pillars"],
}
QUESTION_INTENT_MAP = {
    "obligation": ["obligatoire", "obligation", "required", "obligatory", "must"],
    "prohibition": [
        "interdit",
        "interdits",
        "interdite",
        "interdites",
        "forbidden",
        "prohibited",
        "haram",
    ],
}
TOPIC_METADATA = {
    "prayer": {
        "label": "la priere",
        "obligation": "Oui, la priere est une obligation fondamentale en islam.",
    },
    "fasting": {
        "label": "le jeune du Ramadan",
        "obligation": "Oui, le jeune du Ramadan est une obligation fondamentale en islam.",
    },
    "interest": {
        "label": "les interets usuraires, le riba",
        "prohibition": "Oui, les interets usuraires, le riba, sont interdits en islam.",
    },
    "pillars": {
        "label": "les cinq piliers de l'islam",
    },
}


def _localize_chunks(chunks: list[dict[str, str]]) -> list[dict[str, str]]:
    localized_chunks: list[dict[str, str]] = []
    for chunk in chunks:
        localized_chunk = dict(chunk)
        localized_chunk["original_content"] = chunk["content"]
        if chunk["type"] != "quran":
            localized_chunk["content"] = translate_text_to_french(chunk["content"])
        localized_chunks.append(localized_chunk)
    return localized_chunks


def build_rag_prompt(payload: ChatRequest, chunks: list[dict[str, str]]) -> str:
    context_block = "\n".join(
        f"- [{chunk['type']}] {chunk['source']} ({chunk['ref']}): {chunk['content']}"
        for chunk in chunks
    )
    has_quran = any(chunk["type"] == "quran" for chunk in chunks)

    return (
        "Tu es un assistant islamique francophone.\n"
        "Reponds clairement en francais.\n"
        "Cite uniquement les preuves presentes dans le contexte.\n"
        "Priorite absolue: verifier d'abord le Coran. Puis utiliser les hadiths. Puis le tafsir comme appui explicatif.\n"
        "Si un verset coranique pertinent est present, la conclusion principale doit partir de ce verset.\n"
        "N'inverse jamais cette hierarchie.\n"
        "Traduis en francais les extraits anglais utilises dans ta reponse.\n"
        "Si tu recopies un extrait arabe, il doit etre reproduit exactement sans alteration.\n"
        "Structure attendue: 2 a 4 phrases de reponse directe en francais, sans markdown.\n"
        "Ne genere pas de section 'Sources', de listes, ni de repetition des references: l'interface affiche deja les sources separement.\n"
        "Si aucune preuve explicite n'est presente dans le contexte, reponds exactement: "
        "\"Je n'ai pas de preuve explicite dans le Coran, les hadiths ou le tafsir pour cette question.\"\n"
        f"Presence d'un verset coranique pertinent dans le contexte: {'oui' if has_quran else 'non'}.\n"
        f"Mode demande: {payload.mode}\n"
        f"Ecole juridique: {payload.profile.legal_school}\n"
        f"Langue preferee: {payload.profile.language}\n"
        f"Question: {payload.question}\n"
        "Contexte RAG:\n"
        f"{context_block}"
    )


def _normalize_question(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    normalized = normalized.encode("ascii", "ignore").decode("ascii").lower()
    normalized = re.sub(r"[^a-z0-9\s]", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def _detect_topic(question: str) -> str | None:
    for topic, terms in QUESTION_TOPIC_MAP.items():
        if any(term in question for term in terms):
            return topic
    return None


def _detect_intent(question: str) -> str | None:
    for intent, terms in QUESTION_INTENT_MAP.items():
        if any(term in question for term in terms):
            return intent
    if any(term in question for term in ("quels", "quelles", "liste", "list", "what are", "what is")):
        return "definition"
    return None


def _chunk_matches_topic(chunk: dict[str, str], topic: str) -> bool:
    if topic in chunk.get("tags", []):
        return True

    searchable = _normalize_question(
        " ".join(
            filter(
                None,
                [
                    chunk.get("ref", ""),
                    chunk.get("source", ""),
                    chunk.get("content", ""),
                    chunk.get("original_content", ""),
                    chunk.get("arabic", ""),
                ],
            )
        )
    )
    return any(term in searchable for term in QUESTION_TOPIC_MAP.get(topic, []))


def _sort_chunks_by_priority(chunks: list[dict[str, str]]) -> list[dict[str, str]]:
    return sorted(chunks, key=lambda chunk: SOURCE_PRIORITY.index(chunk["type"]))


def _filter_chunks_for_topic(payload: ChatRequest, chunks: list[dict[str, str]]) -> list[dict[str, str]]:
    topic = _detect_topic(_normalize_question(payload.question))
    if not topic:
        return chunks

    tagged_chunks = [chunk for chunk in chunks if topic in chunk.get("tags", [])]
    if tagged_chunks:
        return _sort_chunks_by_priority(tagged_chunks)

    fallback_chunks = [chunk for chunk in chunks if _chunk_matches_topic(chunk, topic)]
    if fallback_chunks:
        return _sort_chunks_by_priority(fallback_chunks)

    return chunks


def _build_rule_based_answer(payload: ChatRequest, chunks: list[dict[str, str]]) -> str | None:
    question = _normalize_question(payload.question)
    topic = _detect_topic(question)
    intent = _detect_intent(question)
    if not topic or not intent:
        return None

    relevant_chunks = [
        chunk
        for chunk in chunks
        if chunk["type"] in SOURCE_PRIORITY and _chunk_matches_topic(chunk, topic)
    ]
    if not relevant_chunks:
        return "Je n'ai pas de preuve explicite dans le Coran, les hadiths ou le tafsir pour cette question."

    prioritized_chunks = _sort_chunks_by_priority(relevant_chunks)
    if topic == "pillars":
        hadith_chunk = next((chunk for chunk in prioritized_chunks if chunk["type"] == "hadith"), None)
        if hadith_chunk:
            return (
                "Les cinq piliers de l'islam sont l'attestation de foi, la priere, la zakat, le jeune du Ramadan et le pelerinage a La Mecque pour celui qui en a la capacite. "
                f"La preuve principale retrouvee ici vient du hadith ({hadith_chunk['ref']}), qui dit que l'islam est bati sur cinq piliers. "
                "Le Coran detaille ensuite plusieurs de ces obligations separement, mais cette enumeration canonique complete vient d'abord du hadith."
            )

    top_chunk = prioritized_chunks[0]
    topic_meta = TOPIC_METADATA.get(topic, {})
    lead_sentence = topic_meta.get(intent)

    if top_chunk["type"] == "quran" and lead_sentence:
        connector = (
            f"Le Coran l'etablit explicitement en {top_chunk['ref']}, ce qui en fait la preuve principale. "
            if intent == "obligation"
            else f"Le Coran le condamne explicitement en {top_chunk['ref']}, ce qui en fait la preuve principale. "
        )
        return (
            f"{lead_sentence} "
            f"{connector}"
            "Les hadiths et le tafsir peuvent ensuite expliquer les modalites ou appuyer le sens, "
            "mais la preuve principale vient d'abord du Coran."
        )

    source_label = (
        "le Coran"
        if top_chunk["type"] == "quran"
        else "un hadith"
        if top_chunk["type"] == "hadith"
        else "le tafsir"
    )
    return (
        f"Je n'ai pas de verset coranique explicite prioritaire dans le contexte pour conclure de maniere definitive. "
        f"La source la plus pertinente retrouvee ici est {source_label} ({top_chunk['ref']})."
    )

    return None


def _build_sources_from_chunks(chunks: list[dict[str, str]]) -> list[SourceItem]:
    role_by_type = {
        "quran": "Texte source coranique retourne par le retriever.",
        "tafsir": "Explication savante retournee par le retriever.",
        "hadith": "Hadith retourne par le retriever.",
    }
    type_priority = {"quran": 0, "hadith": 1, "tafsir": 2}
    ordered_chunks = sorted(chunks, key=lambda chunk: type_priority.get(chunk["type"], 9))
    return [
        SourceItem(
            type=chunk["type"],
            ref=chunk["ref"],
            text=chunk["content"],
            source=chunk.get("source"),
            arabic=chunk.get("arabic"),
            original_text=chunk.get("original_content"),
            tags=chunk.get("tags", []),
            role=role_by_type.get(chunk["type"], "Source retournee par le retriever."),
        )
        for chunk in ordered_chunks
    ]


def run_rag_pipeline(payload: ChatRequest) -> ChatResponse:
    """Pipeline RAG: retrieval, construction du prompt, generation."""
    chunks = retrieve_relevant_chunks(query=payload.question, top_k=5)
    chunks = _filter_chunks_for_topic(payload=payload, chunks=chunks)[:3]
    if not chunks:
        return ChatResponse(
            answer="Je n'ai pas de preuve explicite dans le Coran, les hadiths ou le tafsir pour cette question.",
            sources=[],
        )

    localized_chunks = _localize_chunks(chunks)
    direct_answer = _build_rule_based_answer(payload=payload, chunks=localized_chunks)
    if direct_answer:
        answer = direct_answer
    else:
        prompt = build_rag_prompt(payload=payload, chunks=localized_chunks)
        generated = generate_answer(prompt=prompt, context_chunks=chunks)
        answer = generated["answer"]

    return ChatResponse(
        answer=answer,
        sources=_build_sources_from_chunks(localized_chunks),
    )
