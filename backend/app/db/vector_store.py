import re
import unicodedata

from app.db.datasets_loader import (
    get_quran_verses,
    load_hadith_datasets,
    load_ibn_kathir_tafsir_dataset,
    load_islamqa_dataset,
    load_seerah_dataset,
)


def _strip_html(html: str) -> str:
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _get_tafsir_text(item: object) -> str:
    if isinstance(item, dict):
        return str(item.get("text", ""))
    if isinstance(item, str):
        return item
    return ""


STOPWORDS = {
    "about",
    "after",
    "ainsi",
    "allah",
    "alors",
    "avec",
    "avoir",
    "cela",
    "ceci",
    "comme",
    "comment",
    "dans",
    "des",
    "dit",
    "elle",
    "elles",
    "entre",
    "est",
    "etaient",
    "etre",
    "font",
    "for",
    "from",
    "hadith",
    "il",
    "ils",
    "islam",
    "les",
    "leur",
    "mais",
    "meme",
    "nous",
    "ont",
    "our",
    "par",
    "pas",
    "plus",
    "pour",
    "pourquoi",
    "que",
    "quel",
    "quelle",
    "quelles",
    "quels",
    "qui",
    "quoi",
    "sa",
    "ses",
    "son",
    "sont",
    "sur",
    "tafsir",
    "the",
    "une",
    "verset",
    "versets",
    "what",
}

QUERY_EXPANSIONS = {
    "coran": {"quran"},
    "quran": {"coran"},
    "epreuve": {"trial", "test", "affliction"},
    "epreuves": {"trials", "tests", "afflictions"},
    "patience": {"patient", "perseverance", "sabr"},
    "patient": {"patience", "sabr"},
    "croyant": {"believer"},
    "croyants": {"believers"},
    "priere": {"prayer", "salat"},
    "salat": {"priere", "prayer"},
    "prayer": {"priere", "salat", "salah"},
    "prieree": {"prayer", "salat", "salah"},
    "obligatoire": {"obligatory", "required", "duty", "must"},
    "obligation": {"obligatory", "required", "duty", "must"},
    "obligatory": {"obligatoire", "obligation", "required"},
    "salat": {"priere", "prayer", "salah"},
    "salah": {"priere", "prayer", "salat"},
    "jeune": {"fast", "fasting", "siyam", "sawm"},
    "jeunee": {"fast", "fasting", "siyam", "sawm"},
    "fasting": {"jeune", "siyam", "sawm"},
    "fast": {"jeune", "fasting", "siyam", "sawm"},
    "siyam": {"jeune", "fasting", "fast"},
    "sawm": {"jeune", "fasting", "fast"},
    "interet": {"interest", "usury", "riba"},
    "interets": {"interest", "usury", "riba"},
    "interest": {"interet", "interets", "usury", "riba"},
    "usury": {"interet", "interets", "interest", "riba"},
    "riba": {"interet", "interets", "interest", "usury"},
    "interdit": {"forbidden", "prohibited", "haram"},
    "interdits": {"forbidden", "prohibited", "haram"},
    "interdite": {"forbidden", "prohibited", "haram"},
    "interdites": {"forbidden", "prohibited", "haram"},
    "haram": {"interdit", "interdits", "interdite", "interdites", "forbidden", "prohibited"},
    "pillar": {"pilier", "piliers", "five"},
    "pillars": {"pilier", "piliers", "five"},
    "music": {"musical", "instruments", "song", "singing", "instrument"},
    "musical": {"music", "instruments", "instrument"},
    "assia": {"asiya", "pharaon", "pharaoh", "wife"},
    "asiya": {"assia", "pharaon", "pharaoh", "wife"},
}

QUERY_PHRASE_EXPANSIONS = {
    "priere": {"الصلاة", "as-salah", "as-salat", "prayer", "salat", "salah"},
    "prayer": {"الصلاة", "as-salah", "as-salat", "priere", "salat", "salah"},
    "salat": {"الصلاة", "as-salah", "as-salat", "priere", "prayer"},
    "salah": {"الصلاة", "as-salah", "as-salat", "priere", "prayer"},
    "jeune": {"الصيام", "fasting", "fast", "siyam", "sawm"},
    "fasting": {"الصيام", "jeune", "fast", "siyam", "sawm"},
    "fast": {"الصيام", "jeune", "fasting", "siyam", "sawm"},
    "interet": {"riba", "interest", "usury"},
    "interets": {"riba", "interest", "usury"},
    "interest": {"riba", "interet", "interets", "usury"},
    "usury": {"riba", "interest", "interet", "interets"},
    "riba": {"interest", "usury", "interet", "interets"},
    "obligatoire": {"obligatory", "required", "must", "commanded", "aqimu"},
    "obligation": {"obligatory", "required", "must", "commanded", "aqimu"},
    "interdit": {"forbidden", "prohibited", "haram"},
    "interdits": {"forbidden", "prohibited", "haram"},
    "interdite": {"forbidden", "prohibited", "haram"},
    "interdites": {"forbidden", "prohibited", "haram"},
    "haram": {"forbidden", "prohibited", "interdit", "interdits", "interdite", "interdites"},
    "pilier": {"pillar", "pillars", "built on five", "islam is built on five"},
    "pillars": {"pilier", "piliers", "built on five", "islam is built on five"},
    "music": {"musical instruments", "musical", "instruments", "song", "singing", "music"},
}

TOPIC_TAG_TERMS = {
    "prayer": {
        "priere",
        "prayer",
        "salat",
        "salah",
        "as-salah",
        "as-salat",
        "الصلاة",
        "aqimu",
    },
    "fasting": {
        "jeune",
        "fast",
        "fasting",
        "ramadan",
        "siyam",
        "sawm",
        "الصيام",
    },
    "interest": {
        "interet",
        "interets",
        "interest",
        "usury",
        "riba",
        "الرِّبَا",
        "الربا",
    },
    "pillars": {
        "pilier",
        "piliers",
        "pillar",
        "pillars",
        "built on five",
        "islam is built on five",
    },
}

INTENT_TAG_TERMS = {
    "obligation": {
        "obligatoire",
        "obligation",
        "obligatory",
        "required",
        "must",
        "commanded",
        "kutiba",
        "كُتِبَ",
        "aqimu",
        "أَقِيمُوا",
    },
    "prohibition": {
        "interdit",
        "interdits",
        "interdite",
        "interdites",
        "forbidden",
        "prohibited",
        "haram",
        "warned",
        "harrama",
        "حَرَّمَ",
    },
}


def _normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return ascii_text.lower()


def _normalize_arabic_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(
        char
        for char in normalized
        if not unicodedata.combining(char) and not ("\u064b" <= char <= "\u065f")
    )


def _tokenize(text: str) -> list[str]:
    normalized = _normalize_text(text)
    return [
        token
        for token in re.findall(r"[a-z0-9:]{3,}", normalized)
        if token not in STOPWORDS
    ]


def _infer_tags(
    *,
    ref: str,
    source: str,
    content: str,
    arabic: str = "",
    source_type: str,
) -> list[str]:
    searchable_text = " ".join(filter(None, [ref, source, content, arabic]))
    normalized_searchable = _normalize_text(searchable_text)
    normalized_arabic_searchable = _normalize_arabic_text(searchable_text)
    tags = {source_type}

    for topic, terms in TOPIC_TAG_TERMS.items():
        if any(
            term in normalized_searchable
            or term in searchable_text.lower()
            or term in normalized_arabic_searchable
            for term in terms
        ):
            tags.add(topic)

    for intent, terms in INTENT_TAG_TERMS.items():
        if any(
            term in normalized_searchable
            or term in searchable_text.lower()
            or term in normalized_arabic_searchable
            for term in terms
        ):
            tags.add(intent)

    return sorted(tags)


def _build_query_features(query: str) -> dict[str, object]:
    normalized_query = _normalize_text(query)
    tokens = _tokenize(query)
    token_set = set(tokens)
    expanded_tokens = set(token_set)
    phrase_terms = set()
    for token in token_set:
        expanded_tokens.update(QUERY_EXPANSIONS.get(token, set()))
        phrase_terms.update(QUERY_PHRASE_EXPANSIONS.get(token, set()))
    direct_ref_match = re.search(r"\b(\d{1,3}:\d{1,3})\b", normalized_query)
    mentions_quran = any(term in token_set for term in {"coran", "quran", "sourate"})
    mentions_hadith = any(term in token_set for term in {"sunna", "sunnah", "prophete"})
    mentions_tafsir = "tafsir" in token_set

    return {
        "normalized_query": normalized_query,
        "tokens": tokens,
        "token_set": expanded_tokens,
        "phrase_terms": phrase_terms,
        "direct_ref": direct_ref_match.group(1) if direct_ref_match else None,
        "mentions_quran": mentions_quran,
        "mentions_hadith": mentions_hadith,
        "mentions_tafsir": mentions_tafsir,
    }


def _priority_quran_ref_weights(features: dict[str, object]) -> dict[str, int]:
    token_set = features["token_set"]
    asks_about_prayer = bool({"priere", "prayer", "salat", "salah"}.intersection(token_set))
    asks_about_fasting = bool({"jeune", "fast", "fasting", "siyam", "sawm"}.intersection(token_set))
    asks_about_obligation = bool({"obligatoire", "obligation", "obligatory", "required", "duty", "must"}.intersection(token_set))
    asks_about_interest = bool({"interet", "interets", "interest", "usury", "riba"}.intersection(token_set))
    asks_about_prohibition = bool(
        {"interdit", "interdits", "interdite", "interdites", "forbidden", "prohibited", "haram"}.intersection(token_set)
    )
    if asks_about_prayer and asks_about_obligation:
        return {
            "2:43": 36,
            "2:110": 32,
            "11:114": 28,
            "2:45": 20,
            "2:3": 12,
        }
    if asks_about_fasting and asks_about_obligation:
        return {
            "2:183": 40,
            "2:185": 34,
            "2:184": 24,
        }
    if asks_about_interest and asks_about_prohibition:
        return {
            "2:275": 44,
            "2:278": 40,
            "2:279": 36,
            "3:130": 30,
            "30:39": 18,
        }
    return {}


def _priority_hadith_ref_weights(features: dict[str, object]) -> dict[str, int]:
    token_set = features["token_set"]
    asks_about_pillars = bool({"pilier", "piliers", "pillar", "pillars", "five"}.intersection(token_set))
    if asks_about_pillars:
        return {
            "https://sunnah.com/nasai:5001": 42,
            "Book 47, Hadith 17": 38,
        }
    return {}


def _score_text_match(
    features: dict[str, object],
    searchable_text: str,
    source_type: str,
) -> int:
    query_tokens = features["token_set"]
    phrase_terms = features["phrase_terms"]
    normalized_searchable = _normalize_text(searchable_text)
    normalized_arabic_searchable = _normalize_arabic_text(searchable_text)
    document_tokens = set(_tokenize(searchable_text))
    overlap = len(query_tokens.intersection(document_tokens))
    score = overlap * 4
    phrase_hits = sum(
        1
        for term in phrase_terms
        if term
        and (
            term in searchable_text.lower()
            or term in normalized_searchable
            or term in normalized_arabic_searchable
        )
    )
    score += phrase_hits * 5

    if features["direct_ref"] and features["direct_ref"] in normalized_searchable:
        score += 12

    if overlap == 0 and phrase_hits == 0 and score < 12:
        return 0

    if source_type == "quran" and features["mentions_quran"]:
        score += 6
    if source_type == "tafsir" and (features["mentions_quran"] or features["mentions_tafsir"]):
        score += 4
    if source_type == "hadith" and features["mentions_hadith"]:
        score += 6
    if source_type == "hadith" and features["mentions_quran"] and not features["mentions_hadith"]:
        score -= 4
    if source_type == "quran" and phrase_hits:
        score += 6

    return score


def _search_quran_verses(query: str, top_k: int) -> list[dict[str, str]]:
    verses = get_quran_verses()
    if not verses:
        return []

    features = _build_query_features(query)
    priority_ref_weights = _priority_quran_ref_weights(features)
    if not features["tokens"] and not features["direct_ref"]:
        return []

    matches = []
    for verse in verses:
        translation = verse.get("translation", "")
        searchable_text = f"{verse['ref']} {verse['text']} {translation}"
        score = _score_text_match(features, searchable_text, "quran")
        score += priority_ref_weights.get(verse["ref"], 0)
        if score > 0:
            matches.append(
                {
                    "type": "quran",
                    "source": verse["source"],
                    "ref": verse["ref"],
                    "content": verse["text"],
                    "arabic": verse["text"],
                    "tags": _infer_tags(
                        ref=verse["ref"],
                        source=verse["source"],
                        content=verse["text"],
                        arabic=verse["text"],
                        source_type="quran",
                    ),
                    "score": score,
                }
            )

    matches.sort(key=lambda item: item["score"], reverse=True)
    return [
        {
            "type": item["type"],
            "source": item["source"],
            "ref": item["ref"],
            "content": item["content"],
            "arabic": item["arabic"],
            "tags": item["tags"],
            "lexical_score": item["score"],
        }
        for item in matches[:top_k]
    ]
def get_verse_by_ref(ref_str: str) -> dict[str, str] | None:
    """Récupère un verset spécifique par sa référence exacte (ex: '2:173' ou 'Quran 2:173')."""
    verses = get_quran_verses()
    clean_ref = ref_str.replace("Quran ", "").strip()
    for v in verses:
        if v["ref"] == clean_ref:
            return {
                "type": "quran",
                "source": v["source"],
                "ref": v["ref"],
                "content": v["text"],
                "arabic": v["text"],
                "tags": _infer_tags(
                    ref=v["ref"],
                    source=v["source"],
                    content=v["text"],
                    arabic=v["text"],
                    source_type="quran",
                ),
                "lexical_score": 1.0,
            }
    return None


def _search_tafsir_entries(query: str, top_k: int) -> list[dict[str, str]]:
    dataset = load_ibn_kathir_tafsir_dataset()
    if not dataset:
        return []

    features = _build_query_features(query)
    priority_ref_weights = _priority_quran_ref_weights(features)
    matches = []

    if features["direct_ref"]:
        ref = features["direct_ref"]
        if ref in dataset:
            text = _strip_html(_get_tafsir_text(dataset[ref]))
            if text:
                return [
                    {
                        "type": "tafsir",
                        "source": "Ibn Kathir via Qul/Tarteel",
                        "ref": f"Ibn Kathir {ref}",
                        "content": text[:1800],
                        "tags": _infer_tags(
                            ref=ref,
                            source="Ibn Kathir via Qul/Tarteel",
                            content=text[:1800],
                            source_type="tafsir",
                        ),
                    }
                ]

    if not features["tokens"]:
        return []

    for ref, item in dataset.items():
        plain_text = _strip_html(_get_tafsir_text(item))
        searchable_text = f"{ref} {plain_text}"
        score = _score_text_match(features, searchable_text, "tafsir")
        score += max(priority_ref_weights.get(ref, 0) - 8, 0)
        if score > 0:
            matches.append(
                {
                    "type": "tafsir",
                    "source": "Ibn Kathir via Qul/Tarteel",
                    "ref": f"Ibn Kathir {ref}",
                    "content": plain_text[:1800],
                    "tags": _infer_tags(
                        ref=ref,
                        source="Ibn Kathir via Qul/Tarteel",
                        content=plain_text[:1800],
                        source_type="tafsir",
                    ),
                    "score": score,
                }
            )

    matches.sort(key=lambda item: item["score"], reverse=True)
    return [
        {
            "type": item["type"],
            "source": item["source"],
            "ref": item["ref"],
            "content": item["content"],
            "tags": item["tags"],
            "lexical_score": item["score"],
        }
        for item in matches[:top_k]
    ]


def _search_hadith_entries(query: str, top_k: int) -> list[dict[str, str]]:
    hadith_records = load_hadith_datasets()
    if not hadith_records:
        return []

    features = _build_query_features(query)
    priority_hadith_weights = _priority_hadith_ref_weights(features)
    if not features["tokens"]:
        return []

    matches = []
    for record in hadith_records:
        english_text = record.get("English_Text", "")
        arabic_text = record.get("Arabic_Text", "")
        book = record.get("Book", "")
        reference = record.get("Reference", "")
        in_book_reference = record.get("In-book reference", "")
        searchable_text = f"{book} {reference} {in_book_reference} {english_text} {arabic_text}"
        score = _score_text_match(features, searchable_text, "hadith")
        score += priority_hadith_weights.get(reference, 0)
        score += priority_hadith_weights.get(in_book_reference, 0)
        if features["mentions_quran"] and not features["mentions_hadith"] and score < 8:
            continue

        if score >= 4:
            matches.append(
                {
                    "type": "hadith",
                    "source": book or "Hadith",
                    "ref": reference or in_book_reference or "Hadith reference",
                    "content": english_text[:1800],
                    "arabic": arabic_text[:1800] if arabic_text else "",
                    "tags": _infer_tags(
                        ref=reference or in_book_reference or "Hadith reference",
                        source=book or "Hadith",
                        content=english_text[:1800],
                        arabic=arabic_text[:1800] if arabic_text else "",
                        source_type="hadith",
                    ),
                    "score": score,
                }
            )

    matches.sort(key=lambda item: item["score"], reverse=True)
    return [
        {
            "type": item["type"],
            "source": item["source"],
            "ref": item["ref"],
            "content": item["content"],
            "arabic": item["arabic"],
            "tags": item["tags"],
            "lexical_score": item["score"],
        }
        for item in matches[:top_k]
    ]


def _search_fatwa_entries(query: str, top_k: int) -> list[dict[str, str]]:
    dataset = load_islamqa_dataset()
    if not dataset:
        return []

    features = _build_query_features(query)
    if not features["tokens"]:
        return []

    matches = []
    for item in dataset:
        searchable_text = f"{item['title']} {item['question']} {item['content']}"
        score = _score_text_match(features, searchable_text, "fatwa")
        if score > 0:
            matches.append(
                {
                    "type": "fatwa",
                    "source": item["source"],
                    "ref": f"IslamQA {item['id']}",
                    "content": item["content"][:1800],
                    "url": item.get("url"),
                    "tags": _infer_tags(
                        ref=item["id"],
                        source=item["source"],
                        content=item["title"] + " " + item["question"],
                        source_type="fatwa",
                    ),
                    "score": score,
                }
            )

    matches.sort(key=lambda item: item["score"], reverse=True)
    return [
        {
            "type": item["type"],
            "source": item["source"],
            "ref": item["ref"],
            "content": item["content"],
            "url": item.get("url"),
            "tags": item["tags"],
            "lexical_score": item["score"],
        }
        for item in matches[:top_k]
    ]


def _search_seerah_entries(query: str, top_k: int) -> list[dict[str, str]]:
    dataset = load_seerah_dataset()
    if not dataset:
        return []

    features = _build_query_features(query)
    if not features["tokens"]:
        return []

    matches = []
    for item in dataset:
        searchable_text = f"{item['title']} {item['content']} {item['category']}"
        score = _score_text_match(features, searchable_text, "seerah")
        if score > 0:
            matches.append(
                {
                    "type": "seerah",
                    "source": "Prophetic Biography (Seerah)",
                    "ref": item["id"],
                    "content": item["content"],
                    "tags": _infer_tags(
                        ref=item["id"],
                        source="Seerah",
                        content=item["title"] + " " + item["content"],
                        source_type="seerah",
                    ),
                    "score": score,
                }
            )

    matches.sort(key=lambda item: item["score"], reverse=True)
    return [
        {
            "type": item["type"],
            "source": item["source"],
            "ref": item["ref"],
            "content": item["content"],
            "tags": item["tags"],
            "lexical_score": item["score"],
        }
        for item in matches[:top_k]
    ]


def search_similar_chunks(
    query: str,
    embedding: list[float] | None,
    top_k: int = 3,
) -> list[dict[str, str]]:
    """Preselction lexicale pour alimenter le reranking semantique."""
    quran_matches = _search_quran_verses(query=query, top_k=top_k)
    seerah_matches = _search_seerah_entries(query=query, top_k=top_k)
    tafsir_matches = _search_tafsir_entries(query=query, top_k=top_k)
    hadith_matches = _search_hadith_entries(query=query, top_k=top_k)
    fatwa_matches = _search_fatwa_entries(query=query, top_k=top_k)
    _ = query, embedding
    dynamic_chunks = []
    source_lists = [quran_matches, seerah_matches, hadith_matches, tafsir_matches, fatwa_matches]
    source_index = 0

    while len(dynamic_chunks) < top_k and any(source_lists):
        current_source = source_lists[source_index % len(source_lists)]
        if current_source:
            dynamic_chunks.append(current_source.pop(0))
        source_index += 1

    if dynamic_chunks:
        return dynamic_chunks[:top_k]

    return []
