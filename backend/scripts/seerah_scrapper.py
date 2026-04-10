"""
Scraper - Seerah of Prophet Muhammad ﷺ
Site: https://seerah.gtaf.org/books/4/

SOLUTION FINALE : Le contenu est chargé correctement par Playwright.
On utilise page.inner_text() (texte visible brut) au lieu de BeautifulSoup
pour contourner les classes CSS dynamiques de Next.js.

Dépendances:
    pip install playwright requests beautifulsoup4
    playwright install chromium

Usage:
    python scraper_seerah.py

Sortie:
    seerah.json
"""

import asyncio
import json
import re
from urllib.parse import unquote

import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Page


# ─── Configuration ─────────────────────────────────────────────────────────────

BASE_URL      = "https://seerah.gtaf.org"
BOOK_URL      = f"{BASE_URL}/books/4/"
OUTPUT_FILE   = "seerah.json"
REQUEST_DELAY = 1.5
PAGE_TIMEOUT  = 45_000
HEADLESS      = True


# ─── Phrases à ignorer (navigation, footer…) ──────────────────────────────────

SKIP_LINES = {
    "Seerah of Prophet Muhammad ﷺ",
    "Seerah is a product of Greentech Apps Foundation.",
    "Home", "Prophet", "Donate", "Prophetic Timeline",
    "Play store", "App store", "Get it on",
    "Learn more about us.", "Select option",
    "Pre Prophethood", "Makkan", "Madinan",
}

# Mots-clés qui indiquent une ligne de navigation à ignorer
NAV_KEYWORDS = ("gtaf.org", "greentech", "Play store", "App store", "Get it on")


# ─── Étape 1 : Liste des chapitres ─────────────────────────────────────────────

def fetch_chapter_list() -> list:
    print("📖 Récupération de la liste des chapitres…")
    resp = requests.get(BOOK_URL, timeout=15, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    })
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    chapters, current_era, num = [], "Unknown", 0
    for tag in soup.find_all(["h2", "a"]):
        if tag.name == "h2":
            current_era = tag.get_text(strip=True)
        elif tag.name == "a":
            href = tag.get("href", "")
            m = re.search(r"/chapters/(\d+)/?$", href)
            if not m:
                continue
            title = tag.get_text(strip=True)
            if not title:
                continue
            img = tag.find("img")
            image_url = None
            if img:
                um = re.search(r"url=([^&]+)", img.get("src", ""))
                if um:
                    image_url = unquote(um.group(1))
            num += 1
            chapters.append({
                "chapter_id": int(m.group(1)),
                "number": num,
                "title": title,
                "url": f"{BASE_URL}/books/4/chapters/{m.group(1)}/",
                "era": current_era,
                "image_url": image_url,
            })

    print(f"  ✅ {len(chapters)} chapitres trouvés.\n")
    return chapters


# ─── Étape 2 : Parser le texte brut visible ────────────────────────────────────

def parse_visible_text(raw_text: str, chapter_title: str) -> list:
    """
    Transforme le texte brut (inner_text) en liste d'événements structurés.

    Logique :
    - On ignore les lignes de nav/footer.
    - On détecte les titres de sections = lignes courtes répétées en haut
      (le titre du chapitre apparaît 3-4 fois consécutivement dans le DOM).
    - Le reste est du contenu paragraphe.
    """
    lines = [l.strip() for l in raw_text.splitlines()]
    lines = [l for l in lines if l]  # supprimer lignes vides

    # Filtrer les lignes de navigation/footer
    def is_skip(line: str) -> bool:
        if line in SKIP_LINES:
            return True
        if any(kw in line for kw in NAV_KEYWORDS):
            return True
        if line == chapter_title:
            return True
        return False

    lines = [l for l in lines if not is_skip(l)]

    # Construire les événements
    events = []
    current_title = chapter_title
    current_paragraphs = []

    # Heuristique : une ligne est un TITRE de section si elle est courte
    # (≤ 80 chars) et ne se termine pas par un signe de ponctuation courante
    def looks_like_heading(line: str) -> bool:
        if len(line) > 120:
            return False
        if line.endswith((".", ",", ";", ":", "!", "?")):
            return False
        # Les titres commencent souvent par majuscule et sont sans ponctuation interne lourde
        words = line.split()
        if len(words) < 2 or len(words) > 15:
            return False
        return True

    for line in lines:
        if looks_like_heading(line) and len(line) < 80:
            # Sauvegarder la section précédente si elle a du contenu
            if current_paragraphs:
                events.append({
                    "title": current_title,
                    "content": "\n\n".join(current_paragraphs),
                })
                current_paragraphs = []
            current_title = line
        else:
            if len(line) > 40:
                current_paragraphs.append(line)

    # Dernière section
    if current_paragraphs:
        events.append({
            "title": current_title,
            "content": "\n\n".join(current_paragraphs),
        })

    # Si aucune sous-section détectée, mettre tout sous le titre principal
    if not events and current_paragraphs:
        events.append({
            "title": chapter_title,
            "content": "\n\n".join(current_paragraphs),
        })

    return events


# ─── Étape 3 : Scraper un chapitre ────────────────────────────────────────────

async def scrape_chapter(page: Page, chapter_info: dict) -> dict:
    chapter = {
        "chapter_id": chapter_info["chapter_id"],
        "number": chapter_info["number"],
        "title": chapter_info["title"],
        "url": chapter_info["url"],
        "era": chapter_info["era"],
        "image_url": chapter_info.get("image_url"),
        "events": [],
        "raw_text": "",
    }

    try:
        await page.goto(chapter_info["url"], wait_until="networkidle", timeout=PAGE_TIMEOUT)
        await asyncio.sleep(1.2)

        # Lire le texte visible brut directement — fiable même avec CSS dynamique
        raw_text = await page.inner_text("body")

        events = parse_visible_text(raw_text, chapter_info["title"])
        chapter["events"] = events
        chapter["raw_text"] = "\n\n".join(
            f"### {e['title']}\n{e['content']}" for e in events
        )

    except Exception as exc:
        print(f"\n     ❌ Erreur: {exc}", end="")

    return chapter


# ─── Main ──────────────────────────────────────────────────────────────────────

async def main():
    print("═" * 62)
    print("  🕌  Seerah Scraper v4 — inner_text (texte visible brut)")
    print("═" * 62 + "\n")

    chapter_list = fetch_chapter_list()
    results = []
    success_count = 0

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=HEADLESS)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
            locale="en-US",
            viewport={"width": 1280, "height": 900},
        )
        page = await context.new_page()

        for i, ch_info in enumerate(chapter_list, start=1):
            print(f"  [{i:02d}/{len(chapter_list)}] {ch_info['title'][:52]}…", end=" ", flush=True)

            chapter = await scrape_chapter(page, ch_info)

            n = len(chapter["events"])
            ok = bool(chapter["raw_text"].strip())
            print(f"{'✅' if ok else '⚠️ '} ({n} événement(s))")

            if ok:
                success_count += 1
            results.append(chapter)

            if i < len(chapter_list):
                await asyncio.sleep(REQUEST_DELAY)

        await browser.close()

    # Écriture JSON finale
    output = {
        "source": BOOK_URL,
        "title": "Seerah of Prophet Muhammad ﷺ",
        "book_id": 4,
        "total_chapters": len(results),
        "eras": list(dict.fromkeys(r["era"] for r in results)),
        "chapters": results,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    fail_count = len(results) - success_count
    print()
    print("═" * 62)
    print(f"  💾 Sauvegardé → {OUTPUT_FILE}")
    print(f"  ✅ Réussis : {success_count}  |  ⚠️  Échecs : {fail_count}")
    if fail_count:
        print(f"  💡 Relancez avec HEADLESS=False pour déboguer les {fail_count} chapitres vides.")
    print("═" * 62)


if __name__ == "__main__":
    asyncio.run(main())