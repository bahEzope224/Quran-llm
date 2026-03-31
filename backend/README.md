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
- `services/retriever.py` cree un embedding puis interroge le vector store
- `services/rag_pipeline.py` construit le prompt RAG avec les chunks recuperes
- `services/llm.py` simule ensuite la generation de la reponse finale

### `GET /user/profile`

Retourne un profil utilisateur mocke pour connecter l'ecran profil du frontend.
