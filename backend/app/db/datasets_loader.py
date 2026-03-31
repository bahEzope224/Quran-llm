import json
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parents[2] / "data"
TANZIL_QURAN_JSON = DATA_DIR / "tanzil_quran_simple.json"
IBN_KATHIR_TAFSIR_JSON = DATA_DIR / "en-tafisr-ibn-kathir.json"
HADITH_COLLECTION_FILES = [
    "Jami` at-Tirmidhi.json",
    "Sahih Muslim.json",
    "Sahih al-Bukhari.json",
    "Sunan Abi Dawud.json",
    "Sunan Ibn Majah.json",
    "Sunan an-Nasa'i.json",
]


def list_available_datasets() -> list[str]:
    """Liste les datasets presents dans le dossier data."""
    return sorted(path.name for path in DATA_DIR.iterdir()) if DATA_DIR.exists() else []


def load_tanzil_quran_dataset() -> dict:
    """Charge le dataset Coran Tanzil converti en JSON."""
    if not TANZIL_QURAN_JSON.exists():
        return {}

    return json.loads(TANZIL_QURAN_JSON.read_text(encoding="utf-8"))


def get_quran_verses() -> list[dict]:
    """Retourne la liste des versets si le dataset Tanzil est disponible."""
    dataset = load_tanzil_quran_dataset()
    return dataset.get("verses", []) if dataset else []


def load_ibn_kathir_tafsir_dataset() -> dict[str, dict]:
    """Charge le dataset tafsir Ibn Kathir local si disponible."""
    if not IBN_KATHIR_TAFSIR_JSON.exists():
        return {}

    return json.loads(IBN_KATHIR_TAFSIR_JSON.read_text(encoding="utf-8"))


def load_hadith_datasets() -> list[dict]:
    """Charge les recueils de hadith JSON telecharges depuis Hugging Face."""
    records: list[dict] = []

    for filename in HADITH_COLLECTION_FILES:
        path = DATA_DIR / filename
        if not path.exists():
            continue

        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            records.extend(payload)

    return records
