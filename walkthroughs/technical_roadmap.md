# ILM AI : Roadmap d'Amélioration du Modèle

Ce document détaille les étapes techniques nécessaires pour transformer ILM AI d'un prototype robuste en une référence technologique pour la science islamique.

## 🏁 Phase 1 (Actuelle) : RAG Multi-Cascades
- **Point Fort** : Récupération précise de segments de texte via Vector Search (Ollama/all-minilm).
- **Garde-fous** : Filtrage thématique et respect systématique des conventions de nommage.
- **Limites** : Le "cerveau" du LLM reste généraliste (Qwen/Llama).

---

## 🚀 Phase 2 : Spécialisation du Modèle (Fine-Tuning)
L'objectif est d'aider le modèle à comprendre le ton et la logique des textes sacrés, même sans recherche externe.
- **Corpus d'Entraînement** : Créer un dataset de haute qualité de questions/réponses basées sur le Fiqh et le Tafsir.
- **Entraînement (LoRA/QLoRA)** : Fine-tuner un modèle de base (ex: Mistral ou Llama 3) sur ce corpus pour éliminer tout ton "commercial" ou "moderne" trop marqué.
- **Optimisation des Embeddings** : Créer un modèle d'embedding spécialisé dans les termes islamiques (transcription vs arabe vs français) pour une recherche encore plus précise.

---

## 📚 Phase 3 : Big Data Sacré (Expansion des Sources)
Pour que l'utilisateur puisse tout vérifier, nous devons couvrir tout le spectre :
- **Hadiths** : Intégration des 6 livres (Kutub al-Sittah) avec chaînes de transmission (Isnad) visibles.
- **Écoles Juridiques** : Ajout d'une option pour filtrer les preuves selon le Madhab (Maliki, Hanafi, Shafi'i, Hanbali).
- **Manuscrits** : OCR sur des ouvrages anciens non numérisés pour rendre accessible la sagesse oubliée.

---

## 🛠 Problèmes à résoudre ensemble
Si vous souhaitez aider, voici nos chantiers ouverts :
1. **Désambiguïsation** : Comment l'IA peut-elle mieux distinguer deux références portant le même nom (ex: Hadith cité dans deux livres différents) ?
2. **Qualité de Traduction** : Passer de la traduction à la volée vers une base de données de traductions officielles certifiées.
3. **Inférence Rapide** : Optimisation pour faire tourner ces modèles lourds avec un temps de réponse < 1 seconde sur des serveurs légers.

---

> "Le savoir est un trésor, la preuve en est la clé."
> Rejoignez-nous pour forger cette clé technologique.
