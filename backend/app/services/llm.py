from app.models.schemas import SourceItem


def generate_answer(prompt: str, context_chunks: list[dict[str, str]]) -> dict[str, object]:
    """Generation mockee de reponse en attendant un vrai LLM open-source."""
    _ = prompt
    return {
        "answer": (
            "La patience est une vertu centrale en Islam. Elle apparait dans le Coran "
            "comme une preuve de sincerite dans l'epreuve, elle est expliquee par les "
            "savants comme une perseverance active, et les hadiths montrent qu'elle "
            "transforme les difficultes en bien pour le croyant."
        ),
        "sources": [
            SourceItem(
                type="quran",
                ref="29:2",
                text="Les gens pensent-ils qu'on les laissera dire : Nous croyons, sans les eprouver ?",
                source="Coran",
                arabic="أَحَسِبَ النَّاسُ أَنْ يُتْرَكُوا أَنْ يَقُولُوا آمَنَّا وَهُمْ لَا يُفْتَنُونَ",
                role="Texte source principal sur l'epreuve et la sincerite de la foi.",
            ),
            SourceItem(
                type="tafsir",
                ref="Ibn Kathir 29:2",
                text=(
                    "L'epreuve distingue la veracite de la foi et appelle a une patience "
                    "active dans la perseverance."
                ),
                source="Tafsir Ibn Kathir",
                role="Explication savante du verset et de sa portee.",
            ),
            SourceItem(
                type="hadith",
                ref="Muslim 2999",
                text=(
                    "L'etonnant est le cas du croyant. Tout ce qui lui arrive est un bien. "
                    "S'il est touche par un malheur, il patiente et c'est un bien pour lui."
                ),
                source="Sahih Muslim",
                role="Confirmation prophetique de la valeur spirituelle de la patience.",
            ),
        ],
        "retrieved_chunks": context_chunks,
    }
