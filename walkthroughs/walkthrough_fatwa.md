# Walkthrough - IslamQA Integration (Fatwa Fallback)

L'intégration d'**IslamQA** comme source de secours est terminée sur la branche `feat-fatwa`.

## Modifications Apportées

### 🕷️ Collecte des Données
- **Scraper Hybride** : Création de `scripts/scrape_islamqa.py`. Une extraction assistée par navigateur a été utilisée pour les premières données de test.
- **Dataset Initial** : Création de `data/islamqa_fatwas.json` contenant des fatwas sur le destin et les invocations (Dhikr).

### 🔍 Moteur de Recherche (Backend)
- **Indexation** : Mise à jour de `datasets_loader.py` pour charger les Fatwas.
- **Recherche Lexicale** : Implémentation de `_search_fatwa_entries` dans `vector_store.py`.

### 🛡️ Logique de Cascade (RAG)
- **Priorité Scripturaire** : Le système a été configuré pour respecter la hiérarchie suivante : **QURAN > HADITH > TAFSIR > FATWA**.
- **Fallback Automatique** : Dans `rag_pipeline.py`, les Fatwas ne sont interrogées que si les scores de pertinence du Coran/Hadith sont inférieurs à un seuil de confiance (0.4).

## Résultats des Tests

### Validation de la Cascade
- [x] **Test de Fallback** : Confirmé par les logs techniques (`DEBUG: Fallback to Fatwa search`).
- [x] **Inclusion des Sources** : Les URLs vers les Fatwas originales sont désormais transmises au Frontend.

> [!TIP]
> Pour enrichir davantage la base, il suffira d'ajouter des URLs dans le script de scraping et de relancer l'import. Le système détectera automatiquement les nouveaux IDs.
