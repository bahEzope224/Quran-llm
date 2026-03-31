# ILM AI Backend

Architecture backend FastAPI pour ILM AI.

## Structure

```text
backend/
├─ app/
│  ├─ main.py
│  ├─ config.py
│  ├─ models/
│  │  └─ schemas.py
│  ├─ services/
│  │  ├─ retriever.py
│  │  ├─ embeddings.py
│  │  ├─ llm.py
│  │  └─ rag_pipeline.py
│  ├─ db/
│  │  ├─ vector_store.py
│  │  └─ datasets_loader.py
│  └─ routes/
│     ├─ chat.py
│     └─ user.py
├─ data/
├─ requirements.txt
└─ README.md
```

## Installation

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration LLM

Le backend peut maintenant appeler un vrai LLM.

Le mode recommande ici est `Ollama` en local, car il est gratuit et simple pour du traitement de texte.

Variables d'environnement supportees:

```bash
export LLM_PROVIDER="ollama"
export LLM_MODEL="llama3.2:1b"
export LLM_BASE_URL="http://127.0.0.1:11434/api/chat"
export LLM_TIMEOUT_SECONDS="30"
export LLM_TEMPERATURE="0.2"
export EMBEDDINGS_PROVIDER="ollama"
export EMBEDDINGS_MODEL="all-minilm"
export EMBEDDINGS_BASE_URL="http://127.0.0.1:11434/api/embed"
export EMBEDDINGS_CANDIDATE_POOL="18"
```

Exemple de demarrage avec Ollama:

```bash
ollama pull llama3.2:1b
ollama pull all-minilm
ollama serve
```

Si Ollama n'est pas lance, le backend garde un mode de secours local:
- retrieval normal sur les datasets
- synthese deterministe des passages retrouves

Si tu veux utiliser une API distante compatible OpenAI, il faut definir:

```bash
export LLM_PROVIDER="openai"
export LLM_API_KEY="sk-..."
export LLM_MODEL="gpt-4.1-mini"
export LLM_BASE_URL="https://api.openai.com/v1/chat/completions"
```

## Lancement

```bash
uvicorn app.main:app --reload
```

API disponible sur `http://127.0.0.1:8000` et documentation sur `http://127.0.0.1:8000/docs`.

## Endpoints

### `POST /chat`

```json
{
  "question": "Quelles sont les vertus de la patience selon le Coran et les hadiths ?",
  "mode": "response",
  "profile": {
    "legal_school": "Maliki",
    "language": "Francais",
    "mode": "Clair",
    "notifications_enabled": true
  }
}
```

Retourne une reponse structuree avec:
- `answer`
- `sources`

Chaque source suit le format:

```json
{
  "type": "quran",
  "ref": "29:2",
  "text": "Les gens pensent-ils qu'on les laissera dire : Nous croyons, sans les eprouver ?",
  "source": "Coran",
  "arabic": "..."
}
```

## Flux RAG

- `routes/chat.py` recoit `question`, `mode` et `profile`
- `services/retriever.py` fait une preselction lexicale puis un reranking semantique via embeddings Ollama
- `services/rag_pipeline.py` construit le prompt RAG avec les chunks recuperes
- `services/llm.py` appelle un LLM distant si configure, sinon utilise un fallback local

## Donnees Coran

Le backend integre maintenant un dataset Coran issu de Tanzil:
- source officielle: https://tanzil.net/download/
- fichier brut: `data/tanzil_quran_simple.xml`
- conversion interne backend: `data/tanzil_quran_simple.json`

Le chargeur est dans [app/db/datasets_loader.py](/Users/ibrahimabah/ilm-quran/backend/app/db/datasets_loader.py) et le retriever Quran utilise ce dataset dans [app/db/vector_store.py](/Users/ibrahimabah/ilm-quran/backend/app/db/vector_store.py).

La page Tanzil indique que le texte peut etre redistribue verbatim, mais ne doit pas etre modifie, et que l'attribution a Tanzil.net doit etre conservee.

## Donnees Tafsir

Le backend peut aussi exploiter un fichier tafsir local:
- `data/en-tafisr-ibn-kathir.json`

Le chargeur local est branche dans [app/db/datasets_loader.py](/Users/ibrahimabah/ilm-quran/backend/app/db/datasets_loader.py) et le retriever peut maintenant retourner des entrees Ibn Kathir depuis [app/db/vector_store.py](/Users/ibrahimabah/ilm-quran/backend/app/db/vector_store.py).

## Donnees Hadith

Le backend integre aussi des recueils de hadith telecharges depuis le dataset Hugging Face:
- `data/Sahih Muslim.json`
- `data/Sahih al-Bukhari.json`
- `data/Jami\` at-Tirmidhi.json`
- `data/Sunan Abi Dawud.json`
- `data/Sunan Ibn Majah.json`
- `data/Sunan an-Nasa'i.json`

Le chargeur lit ces fichiers dans [app/db/datasets_loader.py](/Users/ibrahimabah/ilm-quran/backend/app/db/datasets_loader.py) et le retriever peut maintenant retourner des hadiths depuis [app/db/vector_store.py](/Users/ibrahimabah/ilm-quran/backend/app/db/vector_store.py).

### `GET /user/profile`

Retourne un profil utilisateur mocke pour connecter l'ecran profil du frontend.
