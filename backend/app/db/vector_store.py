def search_similar_chunks(
    query: str,
    embedding: list[float],
    top_k: int = 3,
) -> list[dict[str, str]]:
    """Simulation de recherche vectorielle en attendant FAISS/ChromaDB."""
    chunks = [
        {
            "type": "quran",
            "source": "Coran",
            "ref": "29:2",
            "content": "Les croyants sont eprouves afin que leur sincerite soit manifeste.",
            "arabic": "أَحَسِبَ النَّاسُ أَنْ يُتْرَكُوا أَنْ يَقُولُوا آمَنَّا وَهُمْ لَا يُفْتَنُونَ",
        },
        {
            "type": "tafsir",
            "source": "Tafsir Ibn Kathir",
            "ref": "Ibn Kathir 29:2",
            "content": "L'epreuve distingue la veracite de la foi et appelle a la perseverance.",
        },
        {
            "type": "hadith",
            "source": "Sahih Muslim",
            "ref": "Muslim 2999",
            "content": "Le croyant patiente dans le malheur et cela devient un bien pour lui.",
        },
    ]
    _ = query, embedding
    return chunks[:top_k]
