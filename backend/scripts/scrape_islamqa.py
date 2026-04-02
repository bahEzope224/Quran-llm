import json
import re
import time
from pathlib import Path
from typing import Optional

import httpx
from bs4 import BeautifulSoup

# Configuration
BASE_URL = "https://islamqa.info/fr"
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
OUTPUT_FILE = DATA_DIR / "islamqa_fatwas.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def scrape_fatwa(url: str) -> Optional[dict]:
    """Extrait le contenu d'une page de fatwa IslamQA."""
    print(f"DEBUG: Scraping {url}...")
    try:
        with httpx.Client(headers=HEADERS, timeout=20.0, follow_redirects=True) as client:
            response = client.get(url)
            response.raise_for_status()
            
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extraction du titre (Classe Tailwind specifique)
        title_tag = soup.find("h1", class_=lambda x: x and "tw-font-title" in x)
        title = title_tag.get_text(strip=True) if title_tag else ""
        
        # Extraction de la question (Bloc jauni tw-bg-paper3)
        question_div = soup.find("div", class_=lambda x: x and "tw-bg-paper3" in x)
        question_text = ""
        if question_div:
            content_div = question_div.find(class_="font-content-1")
            question_text = content_div.get_text(strip=True) if content_div else question_div.get_text(strip=True)
            # Nettoyage du prefixe "Question XXXXX"
            question_text = re.sub(r"^Question\s*\d+\s*", "", question_text, flags=re.IGNORECASE)
            
        # Extraction de la réponse (Section apres le H2 "la reponse")
        # On cherche le conteneur de reponse via la classe de police specifique
        answer_text = ""
        answer_header = soup.find("h2", string=lambda s: s and "la r\u00e9ponse" in s.lower())
        if answer_header:
            # La reponse est generalement dans le div suivant avec font-content-1
            parent_section = answer_header.find_parent("section")
            if parent_section:
                content_div = parent_section.find(class_="font-content-1")
                if content_div:
                    answer_text = content_div.get_text(strip=True)
        
        # Fallback si la structure H2/Section echoue
        if not answer_text:
            all_content = soup.find_all(class_="font-content-1")
            if len(all_content) > 1:
                # Souvent le 2eme bloc font-content-1 est la reponse
                answer_text = all_content[-1].get_text(strip=True)

        if not title or not answer_text:
            print(f"WARNING: Contenu incomplet pour {url}")
            return None
            
        # Identification simplifiée des tags depuis l'URL ou le titre
        fatwa_id = url.split("/")[-2] if url.endswith("/") else url.split("/")[-1]
        
        return {
            "id": fatwa_id,
            "title": title,
            "question": question_text,
            "content": answer_text,
            "source": "IslamQA (Fatwa)",
            "url": url,
            "type": "fatwa"
        }
        
    except Exception as e:
        print(f"ERROR: Echec pour {url}: {e}")
        return None

def run_import(urls: list[str]):
    """Lance l'importation sur une liste d'URLs."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    results = []
    # Charger l'existant si possible
    if OUTPUT_FILE.exists():
        try:
            results = json.loads(OUTPUT_FILE.read_text(encoding="utf-8"))
        except:
            results = []

    existing_ids = {r["id"] for r in results}
    
    new_count = 0
    for url in urls:
        fatwa_id = url.split("/")[-2] if url.endswith("/") else url.split("/")[-1]
        if fatwa_id in existing_ids:
            print(f"INFO: Fatwa {fatwa_id} déjà présente, skip.")
            continue
            
        data = scrape_fatwa(url)
        if data:
            results.append(data)
            new_count += 1
            # Petit délai pour être poli
            time.sleep(1.0)
            
    if new_count > 0:
        OUTPUT_FILE.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"SUCCESS: {new_count} nouvelles fatwas importées dans {OUTPUT_FILE}")
    else:
        print("INFO: Aucune nouvelle donnée importée.")

if __name__ == "__main__":
    # Liste de test sur des thématiques variées (Jeûne, Prière, Aqida)
    test_urls = [
        "https://islamqa.info/fr/answers/112113/la-destinee-des-auteurs-de-peches-majuers-morts-non-repentis",
        "https://islamqa.info/fr/answers/1/est-il-permis-de-dire-inch-allah-par-habitudes",
        "https://islamqa.info/fr/answers/217496/sa-mere-lui-interdit-de-jeuner-les-jours-blancs",
        "https://islamqa.info/fr/answers/13444/la-regle-relative-a-une-personne-qui-ne-prie-pas",
        "https://islamqa.info/fr/answers/2340/est-il-permis-de-prier-avec-des-vetements-sales",
    ]
    run_import(test_urls)
