import json
import re
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
ISLAMQA_FATWAS_JSON = DATA_DIR / "islamqa_fatwas.json"
SEERAH_JSON = DATA_DIR / "seerah_muhammad.json"


def list_available_datasets() -> list[str]:
    """Liste les datasets presents dans le dossier data."""
    return sorted(path.name for path in DATA_DIR.iterdir()) if DATA_DIR.exists() else []


def load_tanzil_quran_dataset() -> dict:
    """Charge le dataset Coran Tanzil converti en JSON."""
    if not TANZIL_QURAN_JSON.exists():
        return {}

    return json.loads(TANZIL_QURAN_JSON.read_text(encoding="utf-8"))


def get_quran_verses() -> list[dict]:
    """Retourne la liste des versets enrichis de leur traduction anglaise si disponible."""
    dataset = load_tanzil_quran_dataset()
    verses = dataset.get("verses", []) if dataset else []
    
    # Tentative d'enrichissement avec la traduction anglaise du Tafsir
    tafsir_data = load_ibn_kathir_tafsir_dataset()
    if tafsir_data:
        for verse in verses:
            ref = verse.get("ref")
            if ref in tafsir_data:
                val = tafsir_data[ref]
                if isinstance(val, dict):
                    html_content = val.get("text", "")
                else:
                    html_content = str(val)
                
                # Extraction du texte pur depuis le HTML (Ibn Kathir contient beaucoup de balises)
                match = re.search(r'<p class="en translation"[^>]*>(.*?)</p>', html_content, re.DOTALL)
                if match:
                    verse["translation"] = re.sub(r'<[^>]+>', '', match.group(1)).strip()
                else:
                    # Fallback : premier paragraphe clean
                    first_p = re.search(r'<p[^>]*>(.*?)</p>', html_content, re.DOTALL)
                    if first_p:
                        verse["translation"] = re.sub(r'<[^>]+>', '', first_p.group(1)).strip()[:300]
    
    return verses


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


def load_islamqa_dataset() -> list[dict]:
    """Charge le dataset des fatwas IslamQA scrapées."""
    if not ISLAMQA_FATWAS_JSON.exists():
        return []

    return json.loads(ISLAMQA_FATWAS_JSON.read_text(encoding="utf-8"))


def load_seerah_dataset() -> list[dict]:
    """Charge le dataset de la Sira (biographie du Prophète) et l'aplatit en chunks exploitables."""
    if not SEERAH_JSON.exists():
        return []

    try:
        data = json.loads(SEERAH_JSON.read_text(encoding="utf-8"))
        chapters = data.get("chapters", [])
        flat_items = []
        
        for chap in chapters:
            chap_title = chap.get("title", "Sans titre")
            era = chap.get("era", "Général")
            chap_num = chap.get("number", 0)
            
            for i, event in enumerate(chap.get("events", [])):
                event_title = event.get("title", "")
                content = event.get("content", "")
                
                if content:
                    flat_items.append({
                        "id": f"Seerah-Ch{chap_num}-Ev{i}",
                        "title": f"{chap_title} - {event_title}".strip(" -"),
                        "content": content,
                        "category": era,
                        "chapter": chap_num
                    })
                    
        return flat_items
    except Exception as e:
        print(f"DEBUG: Failed to load Seerah dataset: {e}")
        return []
