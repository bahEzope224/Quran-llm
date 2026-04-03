**✅ Checklist complète avant le lancement de Quran-LLM**

### 1. Repository GitHub & Premiers Pas (obligatoire)

- [ ] **Description du repo** : Ajoute une description claire (ex. : « Assistant IA RAG pour le Saint Coran et les Hadiths »)
- [ ] **Topics / Tags** : Ajoute au minimum : `quran`, `rag`, `llm`, `fastapi`, `islam`, `arabic-nlp`, `hadith`
- [ ] **.env.example** : Crée ce fichier avec toutes les variables nécessaires (`OPENAI_API_KEY`, `GROQ_API_KEY`, `LLM_PROVIDER`, `VECTOR_DB_PATH`, etc.)
- [ ] **LICENSE** : Vérifie que le fichier `LICENSE` est bien présent et correspond à MIT (déjà fait)
- [ ] **Supprimer les fichiers temporaires** : Supprime `.DS_Store` et tout fichier inutile
- [ ] **Créer une Release** : Fais une première release `v1.0.0` avec le tag “Initial Release”
- [ ] **Ajouter des screenshots / GIF** dans le README (interface chat + exemple de réponse avec sources)

### 2. Documentation (déjà très bonne)

- [ ] **README.md** : 
  - Ajoute une section **“Live Demo”** (une fois déployé)
  - Ajoute une section **“Exemples de prompts”**
  - Ajoute un badge de statut (ex. : Railway deploy)
- [ ] **backend/README.md** : Complète-le avec les variables d’environnement et la structure des données
- [ ] **walkthroughs/** : Remplis ce dossier avec 2-3 guides (ex. : “Comment ajouter un nouveau dataset de Tafsir”)
- [ ] **API Documentation** : Teste que `/docs` et `/redoc` sont propres et lisibles

### 3. Qualité du Code & Best Practices

- [ ] **Linting & Formatting** : Ajoute `pre-commit` + `ruff` + `black` (ou `isort`)
- [ ] **Type hints** : Vérifie que tout le backend est bien typé (FastAPI + Pydantic)
- [ ] **Dockerfile** : Teste-le en local (`docker build -t quran-llm .` + `docker run`)
- [ ] **.gitignore** : Vérifie qu’il exclut bien `__pycache__`, `.env`, `venv`, `data/vectorstore/`, etc.
- [ ] **Logs & Error Handling** : Ajoute un logging structuré (structlog ou loguru)

### 4. Tests (très important avant lancement public)

- [ ] **Tests unitaires** : Crée un dossier `tests/` avec pytest pour les services RAG
- [ ] **Tests d’intégration** : Teste le endpoint `/chat` avec différentes questions (Coran seul, Hadiths, Tafsir)
- [ ] **Tests de précision RAG** : 
  - Vérifie que les sources citées sont **correctes** (sourate + verset exact)
  - Teste au moins 20 questions critiques (risque d’hallucination sur des sujets religieux)
- [ ] **Test de sécurité** : Vérifie que les réponses restent respectueuses et neutres

### 5. Sécurité & Confidentialité

- [ ] **Gestion des clés API** : Jamais de clés en dur → tout dans `.env`
- [ ] **Rate Limiting** : Ajoute un middleware de limitation de requêtes (surtout si tu utilises un LLM payant)
- [ ] **CORS** : Configure correctement pour le frontend
- [ ] **Protection des données** : Aucune donnée utilisateur stockée sans consentement explicite
- [ ] **Prompt Guardrails** : Ajoute un filtre pour éviter les questions sensibles ou offensantes

### 6. Déploiement (tu es déjà bien parti)

- [ ] **Railway / Docker** : Déploie en staging et teste en conditions réelles
- [ ] **Variables d’environnement sur Railway** : Configure toutes les vars via le dashboard
- [ ] **Base de données vectorielle** : Assure-toi que le vector store est persistant (pas seulement en mémoire)
- [ ] **Frontend** : 
  - Complète le dossier `frontend/` (même si c’est un simple Vite + React)
  - Déploie-le (Vercel / Netlify / Railway)
- [ ] **URL publique** : Ajoute le lien de la démo dans le README

### 7. Aspects Légaux & Éthiques (critiques pour un projet Coran)

- [ ] **Sources des données** : Vérifie que les datasets Coran + Hadiths + Tafsir Ibn Kathir sont **licence-compatible** (open source ou public domain)
- [ ] **Mention légale** : Ajoute dans le README et dans l’interface :  
  « Ce projet n’est pas une fatwa. Les réponses sont générées par IA et doivent être vérifiées par des sources authentiques. »
- [ ] **Disclaimer religieux** : Ajoute une note claire : « Que Allah accepte cette œuvre et la rende bénéfique pour la Oummah »
- [ ] **Conformité RGPD** (si utilisateurs européens) : Politique de confidentialité simple

### 8. Performance RAG & Qualité IA

- [ ] **Chunking & Embedding** : Vérifie que les chunks sont optimaux (300-500 tokens)
- [ ] **Retrieval quality** : Teste le recall (les bons versets remontent-ils ?)
- [ ] **Prompt engineering** : Optimise le system prompt pour qu’il soit toujours pieux et précis
- [ ] **Choix du LLM** : Décide du modèle final (ex. : Llama-3.1-70B, Groq, ou local) et documente-le
- [ ] **Mode “Coran uniquement”** vs “Coran + Hadiths + Tafsir” : Teste les deux modes

### 9. Lancement & Communication

- [ ] **Annonce LinkedIn / X / Reddit** : Prépare un post de lancement
- [ ] **Communauté** : Crée un canal Discord/Telegram pour les retours
- [ ] **Contributeurs** : Ajoute la section “Contributeurs” dans le README
- [ ] **Roadmap** : Crée un fichier `ROADMAP.md` avec les prochaines fonctionnalités (ex. : recherche par sourate, mode audio, etc.)


