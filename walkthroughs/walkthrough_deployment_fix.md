# Walkthrough - Railway Deployment Fix (Monorepo)

Cette intervention corrige l'erreur de build **"Railpack"** rencontrée sur Railway en configurant explicitement le déploiement du backend.

## Changements Effectués

### 1. 📂 Routage Monorepo (`railway.json`)
- Création d'un fichier à la racine pour indiquer à Railway d'utiliser le `Dockerfile` situé dans `/backend`.
- Suppression de la détection automatique "Railpack" au profit d'un build Docker déterministe.

### 2. ⚡ Port Dynamique (`backend/Dockerfile`)
- Modification de la commande de lancement (`CMD`) pour écouter sur la variable `${PORT}` fournie par l'infrastructure Railway.
- Ajout d'une valeur de repli (`8000`) pour le développement local.

### 3. 📦 Dépendances (`backend/requirements.txt`)
- Ajout des bibliothèques de production manquantes :
  - `openai` (pour la communication avec Groq/OpenAI).
  - `beautifulsoup4` (pour le parsing HTML des sources).
  - `jinja2` & `lxml`.

## Étapes de Déploiement

1.  **Push sur Main** : Une fois ces fichiers envoyés, Railway relancera le build.
2.  **Variables d'Environnement** : Assurez-vous d'avoir configuré les clés suivantes dans le dashboard Railway :
    - `LLM_PROVIDER=openai`
    - `LLM_API_KEY=votre_cle_groq`
    - `LLM_BASE_URL=https://api.groq.com/openai/v1/chat/completions`
    - `LLM_MODEL=llama3-70b-8192` (ou le modèle de votre choix).

> [!TIP]
> Ne configurez pas plus de 4 workers (`-w 4`) sur Railway si vous utilisez une instance avec peu de RAM pour éviter les erreurs d'Out-of-Memory (OOM).
