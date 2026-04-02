# Walkthrough - Déploiement Online (Quran-LLM)

L'application est maintenant entièrement préparée pour quitter votre Mac et être déployée sur le Web.

## Changements Majeurs pour la Production

### 1. Le Cœur : Backend Dockerisé
- **Dockerfile** : Nous avons créé une image Python légère qui inclut FastAPI, Gunicorn (pour la stabilité) et tous vos datasets JSON.
- **Isolation** : L'app peut maintenant tourner sur n'importe quel service cloud (Railway, Render, Fly.io).

### 2. L'Intelligence : Cloud-Ready (Groq/OpenAI)
- **Multi-Provider** : Le moteur `llm.py` et `embeddings.py` a été mis à jour. En production, vous pouvez utiliser l'API **Groq** (extrêmement rapide et gratuite) au lieu d'Ollama.
- **Vitesse** : Llama 3 tourne à des centaines de tokens par seconde sur Groq, garantissant une expérience fluide en ligne.

### 3. Le Frontend : Configuration Dynamique
- **Variable d'Environnement** : L'URL de l'API dans `ChatPage.jsx` n'est plus fixée sur `localhost`. Elle s'adaptera automatiquement via la variable `VITE_API_BASE_URL`.

---

## Guide de Mise en Ligne (Utilisation)

### Étape 1 : Le Backend (Exemple sur Railway)
1. Créez un projet sur **Railway.app**.
2. Liez votre repo Git (sous-dossier `/backend`).
3. Ajoutez les variables d'environnement (voir `backend/.env.example`) :
   - `LLM_PROVIDER=openai`
   - `LLM_API_KEY=gsk_votre_cle_groq_ici`
   - `LLM_BASE_URL=https://api.groq.com/openai/v1/chat/completions`

### Étape 2 : Le Frontend (Sur Vercel)
1. Créez un projet sur **Vercel**.
2. Liez votre repo Git (sous-dossier `/frontend`).
3. Ajoutez la variable d'environnement :
   - `VITE_API_BASE_URL=https://votre-backend-railway.app`

### Étape 3 : La Persistance (Feedback)
Le fichier `feedback.jsonl` est stocké localement dans le conteneur. 
> [!TIP]
> Pour garder les feedbacks après un redémarrage, configurez un **Volume** (ex: `/app/data`) dans Railway ou Render.

---

## Prochaines Étapes
Une fois déployé, vous pourrez partager l'URL Vercel avec vos utilisateurs. Vos feedbacks seront collectés sur votre serveur cloud, prêts pour la prochaine phase d'amélioration du moteur !
