"""
Service de traduction française du Coran.

Charge le fichier French_quran.csv (format: sourate|verset|texte) une seule fois
en mémoire et expose une fonction `get_french_verse(ref)` qui retourne la
traduction française officielle à partir d'une référence de type "2:43".
"""

from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
FRENCH_QURAN_CSV = DATA_DIR / "French_quran.csv"

# Cache global — chargé paresseusement au premier appel
_FRENCH_QURAN: dict[str, str] | None = None


def _load_french_quran() -> dict[str, str]:
    """Charge le CSV et retourne un dict {ref: traduction}, ex: {"2:43": "..."}."""
    global _FRENCH_QURAN
    if _FRENCH_QURAN is not None:
        return _FRENCH_QURAN

    mapping: dict[str, str] = {}

    if not FRENCH_QURAN_CSV.exists():
        print(f"WARNING: French_quran.csv introuvable à {FRENCH_QURAN_CSV}")
        _FRENCH_QURAN = mapping
        return mapping

    try:
        content = FRENCH_QURAN_CSV.read_text(encoding="utf-8", errors="replace")
        for line in content.splitlines():
            line = line.strip()
            if not line:
                continue
            parts = line.split("|", 2)
            if len(parts) != 3:
                continue
            sourate, verset, texte = parts
            sourate = sourate.strip()
            verset = verset.strip()
            texte = texte.strip()
            if sourate.isdigit() and verset.isdigit():
                ref = f"{int(sourate)}:{int(verset)}"
                mapping[ref] = texte

        print(f"DEBUG: French Quran chargé — {len(mapping)} versets indexés.")
    except Exception as exc:
        print(f"ERROR: Impossible de charger French_quran.csv : {exc}")

    _FRENCH_QURAN = mapping
    return mapping


def get_french_verse(ref: str) -> str | None:
    """
    Retourne la traduction française d'un verset à partir de sa référence.

    Args:
        ref: Référence au format "sourate:verset" (ex: "2:43", "3:185")

    Returns:
        La traduction française ou None si le verset n'est pas trouvé.
    """
    mapping = _load_french_quran()
    return mapping.get(ref)


def enrich_quran_chunk_with_french(chunk: dict) -> dict:
    """
    Enrichit un chunk de type 'quran' avec la traduction française officielle.

    - Conserve le texte arabe dans la clé 'arabic'.
    - Remplace 'content' par la traduction française du CSV.
    - Ajoute 'french_translation' pour usage dans le prompt.
    - Ajoute 'translation_source' pour identifier la provenance.

    Si la traduction n'est pas disponible, le chunk est retourné tel quel.
    """
    if chunk.get("type") != "quran":
        return chunk

    ref = chunk.get("ref", "")
    french_text = get_french_verse(ref)

    if not french_text:
        print(f"DEBUG: [French Quran] Traduction introuvable pour ref='{ref}'")
        return chunk

    enriched = dict(chunk)

    # On conserve l'arabe si déjà présent (text tanzil)
    if not enriched.get("arabic"):
        enriched["arabic"] = chunk.get("content", "")

    # On injecte la traduction française comme contenu principal
    enriched["content"] = french_text
    enriched["french_translation"] = french_text
    enriched["translation_source"] = "Traduction française du Saint Coran (Muhammad Hamidullah / Roi Fahd)"

    print(f"DEBUG: [French Quran] Verset {ref} enrichi — {len(french_text)} chars")
    return enriched


def get_french_translation_block(ref: str) -> str | None:
    """
    Retourne un bloc de texte formaté pour insertion dans le prompt LLM.

    Format : "📖 Coran {ref} (traduction française): {texte}"
    Retourne None si le verset n'est pas trouvé.
    """
    french = get_french_verse(ref)
    if not french:
        return None
    return f"📖 Coran {ref} (traduction française): {french}"
