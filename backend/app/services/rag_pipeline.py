import re
import unicodedata

from app.config import settings
from app.models.schemas import ChatRequest, ChatResponse, SourceItem
from app.services.llm import (
    generate_answer,
    translate_french_to_english,
    translate_text_to_french,
)
from app.services.retriever import retrieve_relevant_chunks

SOURCE_PRIORITY = ["quran", "seerah", "hadith", "tafsir", "fatwa"]
# Map pour la classification des questions
QUESTION_TOPIC_MAP = {
    "prayer": ["priere", "prayer", "salat", "salah", "salata", "assalata", "salawat", "recueillement"],
    "fasting": ["jeune", "fast", "fasting", "siyam", "sawm", "ramadan"],
    "interest": ["interet", "interets", "interest", "usury", "riba"],
    "pillars": ["pilier", "piliers", "pillar", "pillars", "cinq piliers", "five pillars"],
    "music": ["musique", "music", "musical", "instrument", "instruments", "song", "singing"],
    "general": ["islam", "musulman", "muslim", "religion", "dieu", "allah", "prophete", "prophet", "coran", "quran", "hadith", "sunnah", "foi", "faith", "iman", "ihsan", "priere", "hajj", "zakat", "jeune", "fasting", "halal", "haram"],
    "biography": ["vie", "life", "naissance", "birth", "mort", "death", "mariage", "marriage", "epouse", "wife", "age", "biographie", "biography", "khadija", "aisha", "fatima", "décédé", "décès", "décédée", "mourir", "mort", "né", "né à", "born", "died", "passed away", "prophete", "prohete", "muhammad", "quand", "when", "date", "year", "année"],
}

# Map de traduction pour renforcer les mots-cles critiques
KEYWORD_TRANSLATION_MAP = {
    "mariage": "marriage wedding married",
    "épouse": "wife married spouses",
    "khadija": "khadija khadijah",
    "aïcha": "aisha aysha ayesha",
    "age": "age years year how old",
    "né": "born birth birthed",
    "naissance": "born birth birthed",
    "décédé": "death died passed away deceased",
    "mort": "death died passed away deceased",
    "quand": "when time date year",
    "musique": "music musical instruments",
    "piliers": "pillars five",
    "priere": "prayer salat",
    "jeune": "fasting sawm ramadan",
    "zakat": "charity zakat",
    "pelerinage": "pilgrimage hajj",
    "interdit": "forbidden prohibited haram",
    "obligatoire": "mandatory obligatory required",
    "halal": "permissible allowed",
    "haram": "forbidden prohibited",
    "assia": "asiya pharaoh wife",
    "asiya": "assia pharaoh wife",
}
RELEVANCE_THRESHOLD = 0.30  # Plus souple pour all-minilm
SEMANTIC_TRUST_THRESHOLD = 0.60 # Score pour bypasser le pruning
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
    "identification": ["qui est", "qui etait", "qui fut", "who is", "who was", "who were", "identifier"],
}

# Metadonnees pour enrichir les reponses
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
    "music": {
        "label": "la musique",
        "prohibition": "Les Hadiths (traditions prophetiques) font etat d'avertissements severes concernant certains instruments et contextes musicaux.",
    },
}


def _localize_chunks(chunks: list[dict[str, str]], translate_content: bool = True) -> list[dict[str, str]]:
    """Prepare les chunks pour l'affichage (avec traduction proactive pour Tafsir/Hadith)."""
    localized_chunks: list[dict[str, str]] = []
    for chunk in chunks:
        localized_chunk = dict(chunk)
        localized_chunk["original_content"] = chunk["content"]
        
        # Le Coran reste tel quel (versets sources), le reste est traduit par defaut
        is_quran = chunk["type"] == "quran"
        if translate_content and not is_quran:
            # On force la traduction car on sait que Tafsir/Hadith sont en Anglais dans notre DB
            localized_chunk["content"] = translate_text_to_french(chunk["content"], force=True)
            
        localized_chunks.append(localized_chunk)
    return localized_chunks


def build_rag_prompt(payload: ChatRequest, chunks: list[dict[str, str]], english_query: str = "", intent: str | None = None) -> str:
    """Construit le prompt pour l'LLM en incluant les sources pertinentes."""
    # On ne garde que les sources qui mentionnent vraiment le sujet
    context_block = "\n".join(
        f"- [{chunk['type']}] {chunk['source']} ({chunk['ref']}): {chunk['content']}"
        for chunk in chunks
    )

    if intent == "identification":
        return (
            "Tu es un biographe islamique expert (3 a 5 PHRASES).\n"
            "RESUME le personnage de maniere fluide en te basant sur les SOURCES fournies.\n"
            "RIGUEUR ABSOLUE: N'invente AUCUN chiffre, age, date historique ou duree de regne absent des sources.\n"
            "CONSIGNE DE SILENCE: Si une source parle d'un evenement (ex: mariage) mais ne donne pas l'age, dis explicitement que les sources ne precisent pas l'age.\n\n"
            f"SOURCES:\n{context_block}\n\n"
            f"QUESTION: {payload.question}\n"
            "REPONSE: "
        )
    else:
        persona = "Tu es un assistant musulman expert, factuel et TRES CONCIS (1 a 2 phrases)."
        return (
            f"{persona}\n\n"
            "INSTRUCTION CRITIQUE: Ne reponds qu'avec les informations PRESENTES dans les sources.\n"
            "Si la question porte sur un chiffre (age, nombre) absent des sources, declare que l'information n'est pas disponible dans les textes fournis.\n\n"
            f"SOURCES:\n{context_block}\n\n"
            f"QUESTION: {payload.question}\n"
            "REPONSE: "
        )


def _normalize_question(text: str) -> str:
    """Normalise la question pour faciliter la recherche."""
    normalized = unicodedata.normalize("NFKD", text)
    normalized = normalized.encode("ascii", "ignore").decode("ascii").lower()
    normalized = re.sub(r"[^a-z0-9\s]", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def _detect_topic(question: str) -> str | None:
    """Detecte le sujet de la question."""
    for topic, terms in QUESTION_TOPIC_MAP.items():
        if any(term in question for term in terms):
            return topic
    return None


def _detect_intent(question: str) -> str | None:
    """Detecte l'intention de la question."""
    for intent, terms in QUESTION_INTENT_MAP.items():
        if any(term in question for term in terms):
            return intent
    if any(term in question for term in ("quels", "quelles", "liste", "list", "what are", "what is", "decrire", "describe")):
        return "definition"
    return None


def _is_off_topic(question: str) -> bool:
    """Verifie si la question est manifestement etrangere au domaine islamique."""
    # Si on detecte un topic ou un intent connu, ce n'est pas off-topic
    if _detect_topic(question) or _detect_intent(question):
        return False
        
    # Liste de mots-cles "Alerte Hors-Sujet"
    off_topic_indicators = [
        "capital", "capitale", "president", "meteo", "cuisine", "football", "sport", 
        "politique", "bourse", "cinema", "film", "chanson", "voiture", "habitants"
    ]
    
    # Si on a des indicateurs hors-sujet SANS aucun mot-cle islamique, c'est off-topic
    islamic_keywords = ["islam", "religion", "dieu", "allah", "prophete", "coran", "hadith", "sunnah", "foi"]
    normalized_q = question.lower()
    has_off_topic_words = any(word in normalized_q for word in off_topic_indicators)
    has_islamic_words = any(word in normalized_q for word in islamic_keywords)
    
    return has_off_topic_words and not has_islamic_words


def _chunk_matches_topic(chunk: dict[str, str], topic: str) -> bool:
    """Verifie si le chunk correspond au sujet."""
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
    """Trie les chunks par priorite de source."""
    return sorted(chunks, key=lambda chunk: SOURCE_PRIORITY.index(chunk["type"]))


def _filter_chunks_for_topic(payload: ChatRequest, chunks: list[dict[str, str]]) -> list[dict[str, str]]:
    """Trie et filtre les chunks par priorite de source et pertinence thématique."""
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


def _prune_irrelevant_chunks(chunks: list[dict], english_query: str) -> list[dict]:
    """Supprime les sources qui n'ont aucun rapport lexical avec la question (Securite anti-hallucination)."""
    keywords = set(re.findall(r"\w{4,}", english_query.lower()))
    if not keywords:
        return chunks

    pruned = []
    noise_patterns = ["rain", "mud", "slush", "houses", "fever", "travel"]
    is_obligation = any(kw in english_query.lower() for kw in ["obligatory", "mandatory", "must", "order"])
    # Detection de l'intention "Chiffres/Dates"
    wants_number = any(kw in english_query.lower() for kw in ["age", "year", "how many", "how old", "number", "date", "when", "born", "died"])

    for chunk in chunks:
        if chunk.get("type") == "quran":
            pruned.append(chunk)
            continue
            
        content = (chunk.get("content", "") + " " + chunk.get("ref", "")).lower()
        
        # Filtre de bruit pour les Hadiths en contexte d'obligation generale
        if chunk.get("type") == "hadith" and is_obligation:
            if any(noise in content for noise in noise_patterns):
                continue

        # Si on veut un chiffre et que le chunk n'en contient aucun (regexp simple), on mefie
        if wants_number and not re.search(r"\d+", content):
            # On ne prune pas si le score est EXTREMEMENT eleve (fallback secu)
            if chunk.get("semantic_score", 0) < 0.6:
                print(f"DEBUG: Pruning chunk {chunk['ref']} because it lacks numerical data for a numerical query")
                continue

        # Si le score est tres eleve, on garde (confiance semantique)
        if chunk.get("semantic_score", 0) > 0.8:
            pruned.append(chunk)
            continue
            
        # Sinon, verification de presence de mots-cles
        if any(kw in content for kw in keywords):
            pruned.append(chunk)
            
    return pruned


def _build_rule_based_answer(payload: ChatRequest, chunks: list[dict[str, str]]) -> str | None:
    """Construit une reponse basee sur des regles."""
    question = _normalize_question(payload.question)
    topic = _detect_topic(question)
    intent = _detect_intent(question)
    if not topic or not intent:
        return None

    relevant_chunks = [
        chunk
        for chunk in chunks
        if chunk["type"] in SOURCE_PRIORITY and (
            _chunk_matches_topic(chunk, topic) or chunk["type"] == "quran"
        )
    ]
    if not relevant_chunks:
        return "Je n'ai pas de preuve explicite dans le Coran, les hadiths ou le tafsir pour cette question."

    # On verifie la presence scripturaire sur les chunks RELEVANT
    has_quran = any(c["type"] == "quran" for c in relevant_chunks)
    has_hadith = any(c["type"] == "hadith" for c in relevant_chunks)

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

    if has_quran and has_hadith and lead_sentence:
        q_ref = next(c["ref"] for c in prioritized_chunks if c["type"] == "quran")
        h_ref = next(c["ref"] for c in prioritized_chunks if c["type"] == "hadith")
        return (
            f"{lead_sentence} "
            f"Cette obligation est etablie par le Coran (ex: {q_ref}) et detaillee par les hadiths (ex: {h_ref}). "
            "Les deux sources concordent pour en faire un pilier central de la foi musulmane."
        )

    if top_chunk["type"] == "hadith" and lead_sentence:
        # On ne dit "Coran silencieux" que si on n'a VRAIMENT aucun chunk Quran
        silent_quran = "Bien que le Coran ne le mentionne pas explicitement, " if not has_quran else ""
        return (
            f"{lead_sentence} "
            f"{silent_quran}le hadith ({top_chunk['ref']}) est tres clair sur ce point dans le contexte fourni. "
            "Les savants se basent souvent sur ces traditions pour etablir les regles quand le texte coranique est silencieux."
        )

    # Si c'est une identification (Qui est...), on laisse le LLM faire la bio
    if intent == "identification":
        return None

    source_label = (
        "le Coran"
        if top_chunk["type"] == "quran"
        else "un hadith"
        if top_chunk["type"] == "hadith"
        else "le tafsir"
    )
    # Phrase de repli plus équilibrée
    return (
        f"D'apres les sources disponibles ({source_label} - {top_chunk['ref']}), "
        "une indication est fournie sur ce sujet, bien qu'un verset coranique direct ne soit pas cite ici."
    )


def _build_sources_from_chunks(chunks: list[dict[str, str]]) -> list[SourceItem]:
    """Construit les sources a partir des chunks."""
    role_by_type = {
        "quran": "Texte source coranique retourne par le retriever.",
        "tafsir": "Explication savante retournee par le retriever.",
        "hadith": "Hadith retourne par le retriever.",
        "seerah": "Element de la biographie prophetique (Sira) retourne par le retriever.",
        "fatwa": "Avis jurisprudentiel (Fatwa) d'IslamQA utilise comme clarification pratique.",
    }
    type_priority = {"quran": 0, "seerah": 1, "hadith": 2, "tafsir": 3, "fatwa": 4}
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
            url=chunk.get("url"), # Ajout de l'URL pour les Fatwas
            role=role_by_type.get(chunk["type"], "Source retournee par le retriever."),
        )
        for chunk in ordered_chunks
    ]


def run_rag_pipeline(payload: ChatRequest) -> ChatResponse:
    """Pipeline RAG Ameliore: Traduction EN, Retrieval Hybride, Generation FR."""
    # 1. Verification Hors-Sujet
    normalized_q = _normalize_question(payload.question)
    if _is_off_topic(normalized_q):
        return ChatResponse(
            answer="Je suis ILM AI, une intelligence assistante spécialisée sur l'Islam. Veuillez poser des questions en lien avec la foi, la pratique ou l'histoire islamique.",
            sources=[],
        )

    # 2. Traduction de la question (avec Hybridation par mots-cles)
    english_query = translate_french_to_english(payload.question)
    
    # Enrichissement manuel pour pallier les defaillances de traduction
    lower_question = payload.question.lower()
    extra_keywords = []
    for fr_kw, en_kw in KEYWORD_TRANSLATION_MAP.items():
        if fr_kw in lower_question:
            extra_keywords.append(en_kw)
    
    if extra_keywords:
        english_query = f"{english_query} {' '.join(extra_keywords)}"
    
    # --- DEBUT CHIRURGIE LEXICALE (Anti-Confusion Assia/Aicha) ---
    if "assia" in lower_question or "asiya" in lower_question:
        # Si on cherche Assia, on INTERDIT Aisha (pollution lexicale detectee)
        english_query = re.sub(r"\baisha\b", "", english_query, flags=re.IGNORECASE)
        english_query = f"{english_query} pharaoh asiya quran"
    # --- FIN CHIRURGIE LEXICALE ---

    print(f"DEBUG: Original (FR): {payload.question} -> Enhanced (EN): {english_query}")

    # 2. Retrieval avec Deep Search (top_k=15)
    # On analyse le sujet sur la question originale + sa version enrichie (Double Check)
    topic = _detect_topic(normalized_q + " " + english_query.lower())
    raw_chunks = retrieve_relevant_chunks(query=english_query, top_k=15, topic=topic)
    
    # 3. Filtrage de pertinence hybride
    valid_chunks = []
    keywords = set(re.findall(r"\w{4,}", english_query.lower()))
    for c in raw_chunks:
        score = c.get("semantic_score", 0)
        content = (c.get("content", "") + " " + c.get("ref", "")).lower()
        
        # Le SEUIL DU CORAN est desactive car ces sources sont prioritaires
        chunk_type = c.get("type", "tafsir")
        threshold = -1.0 if chunk_type == "quran" else RELEVANCE_THRESHOLD
        
        if score > threshold or (keywords and any(kw in content for kw in keywords)):
            valid_chunks.append(c)
    
    # 4. Elagage par mots-cles additionnel (Nettoyage final)
    pruned_chunks = _prune_irrelevant_chunks(valid_chunks, english_query)
    
    # 5. Filtrage thématique (TOP 3 initial)
    initial_top_chunks = _filter_chunks_for_topic(payload=payload, chunks=pruned_chunks)
    
    # --- RAFFINEMENT DE CONFIANCE (Anti-Bruit radical avec Entity Lock) ---
    if initial_top_chunks:
        best_score = initial_top_chunks[0].get("semantic_score", 0)
        
        # Entity Lock : Si un nom propre ou un fait vital (mort/vie) est detecte, on garde
        entities = ["khadija", "aisha", "aysha", "khadijah", "fatima", "maryam", "assia", "asiya", "muhammad", "death", "born", "died", "age"]
        query_entities = [e for e in entities if e in payload.question.lower()]
        
        if best_score > 0.75:
            # GAP DYNAMIQUE : Si c'est un fait biographique excellent, on devient impitoyable (0.05)
            # sinon on reste sur une marge de securite standard (0.15)
            primary_type = initial_top_chunks[0].get("type")
            gap_threshold = 0.05 if (primary_type == "seerah" and best_score > 0.80) else 0.15
            
            print(f"DEBUG: High Confidence Match ({best_score:.2f}). Gap Threshold: {gap_threshold}")
            
            if len(initial_top_chunks) > 1:
                new_top = [initial_top_chunks[0]]
                
                # On verifie si le meilleur resultat contient deja les noms cites
                best_content = (initial_top_chunks[0].get("content", "") + " " + initial_top_chunks[0].get("source", "")).lower()
                
                # ENTITY LOCK REFINEMENT: On ignore "muhammad" pour le verrouillage s'il est seul
                # car il est present partout. On ne garde une source faible que pour des noms specifiques (ex: Khadija).
                critical_entities = [e for e in query_entities if e != "muhammad"]
                best_has_entity = any(ent in best_content for ent in critical_entities)
                
                for i in range(1, len(initial_top_chunks)):
                    chunk = initial_top_chunks[i]
                    score = chunk.get("semantic_score", 0)
                    content = (chunk.get("content", "") + " " + chunk.get("source", "")).lower()
                    
                    # On garde si c'est EXTREMEMENT proche OU si ca contient une entite critique manquante
                    has_locked_entity = any(ent in content for ent in critical_entities)
                    
                    if (best_score - score) < gap_threshold or (has_locked_entity and not best_has_entity):
                        new_top.append(chunk)
                    else:
                        break
                initial_top_chunks = new_top
            else:
                initial_top_chunks = initial_top_chunks[:1]
        else:
            initial_top_chunks = initial_top_chunks[:3]
    # --- FIN RAFFINEMENT ---

    # 5b. Evaluation de la force des sources scripturaires (Coran/Hadith/Sira)
    has_strong_scripture = any(
        c["type"] in ["quran", "hadith", "seerah"] and c.get("semantic_score", 0) > 0.4
        for c in initial_top_chunks
    )
    
    if not has_strong_scripture and initial_top_chunks:
        from app.db.vector_store import _search_fatwa_entries
        print("DEBUG: Fallback to Fatwa search (Scriptural scores too low)")
        fatwa_matches = _search_fatwa_entries(query=english_query, top_k=2)
        if fatwa_matches:
            # On preserve les sources scripturaires deja trouvees meme si faibles
            scriptures = [c for c in initial_top_chunks if c["type"] in ["quran", "hadith", "seerah"]]
            # On complete avec les fatwas pour arriver a 3
            initial_top_chunks = (scriptures + fatwa_matches)[:3]
            # On retrie pour la forme (Sira prioritisee pour identification)
            initial_top_chunks = _sort_chunks_by_priority(initial_top_chunks)
    
    # 5c. Priorisation BIOGRAPHIQUE finale si intention idenfication
    if _detect_intent(normalized_q) == "identification":
        initial_top_chunks = sorted(initial_top_chunks, key=lambda c: 1 if c["type"] == "seerah" else 2)

    # 6. Couplage Automatique Verset -> Tafsir (Enrichissement)
    final_display_chunks = []
    from app.services.retriever import retrieve_tafsir_by_ref
    
    for chunk in initial_top_chunks:
        final_display_chunks.append(chunk)
        if chunk["type"] == "quran":
            # On cherche le Tafsir associe et on l'ajoute MEME si on depasse 3
            tafsir = retrieve_tafsir_by_ref(chunk["ref"])
            if tafsir:
                # Eviter les doublons si le tafsir etait deja dans le top 3
                if not any(c["ref"] == tafsir["ref"] for c in final_display_chunks):
                    print(f"DEBUG: Auto-coupling Tafsir for {chunk['ref']} (Post-Top3)")
                    final_display_chunks.append(tafsir)

    if not final_display_chunks:
        return ChatResponse(
            answer="Désolé, je n'ai pas trouvé de sources pertinentes pour répondre à cette question aujourd'hui.",
            sources=[],
        )

    # localized_chunks pour l'affichage final
    display_chunks = _localize_chunks(final_display_chunks, translate_content=True)
    
    # 6. Verification de reponse rapide via regles (sur TOUTE la selection pour ne rien rater du Coran)
    direct_answer = _build_rule_based_answer(payload=payload, chunks=pruned_chunks)
    
    if direct_answer:
        answer = direct_answer
    else:
        # 7. Generation contextuelle via LLM
        intent = _detect_intent(_normalize_question(payload.question))
        prompt = build_rag_prompt(
            payload=payload, 
            chunks=final_display_chunks, 
            english_query=english_query, 
            intent=intent
        )
        if intent == "identification" and not direct_answer:
            # Mode Chat (generate_answer) pour le heros, car _generate est trop sec
            # Le persona "biographe fidele" est injecte par build_rag_prompt
            generated = generate_answer(prompt=prompt, context_chunks=final_display_chunks)
            answer = generated["answer"]
        else:
            # Mode normal pour les avis juridiques (obligation/prohibition)
            generated = generate_answer(prompt=prompt, context_chunks=final_display_chunks)
            answer = generated["answer"]

    return ChatResponse(
        answer=answer,
        sources=_build_sources_from_chunks(display_chunks),
    )
