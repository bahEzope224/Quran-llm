


<div align="center">

# 📖 Quran-LLM

**Un assistant intelligent basé sur l'IA pour explorer le Saint Coran et les Hadiths**

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
[![React](https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev) <!-- à adapter si ton frontend est React -->
[![RAG](https://img.shields.io/badge/RAG-Retrieval%20Augmented%20Generation-FF6B6B?style=for-the-badge)]()

</div>

## ✨ À propos du projet

**Quran-LLM** est une application full-stack qui permet aux utilisateurs de poser des questions sur le **Saint Coran** et les **Hadiths** et d'obtenir des réponses précises, sourcées et contextuelles grâce à une architecture **RAG (Retrieval-Augmented Generation)**.

Le système combine :
- Une base vectorielle contenant les versets du Coran et les hadiths
- Des embeddings de haute qualité
- Un modèle de langage (LLM) pour générer des réponses structurées et fiables
- Des citations précises (sourate, verset, texte arabe, traduction, etc.)

---

## 🚀 Fonctionnalités

- **Chat intelligent** sur le Coran et les Hadiths
- **Mode de réponse configurable** (ex. : focus Coran uniquement, Coran + Hadiths, etc.)
- **Réponses structurées** avec sources vérifiables
- **Profil utilisateur** (mock pour le moment)
- **Architecture RAG** pour une grande précision et réduction des hallucinations
- Interface frontend moderne et responsive

---

## 🛠️ Stack Technique

### Backend
- **Framework** : FastAPI (Python)
- **RAG Pipeline** : LangChain / custom
- **Vector Store** : FAISS ou ChromaDB
- **Embeddings** : Sentence-Transformers
- **LLM** : Intégration flexible (OpenAI, Groq, Ollama, Hugging Face, etc.)

### Frontend
- Technologies : JavaScript + CSS (structure à compléter selon ton framework : React, Vite, etc.)

---

## 📁 Structure du projet

```bash
Quran-LLM/
├── backend/
│   ├── app/
│   │   ├── main.py                 # Point d'entrée FastAPI
│   │   ├── config.py
│   │   ├── models/
│   │   ├── services/               # retriever, embeddings, llm, rag_pipeline
│   │   ├── db/                     # vector_store, datasets_loader
│   │   └── routes/                 # chat.py, user.py
│   ├── data/                       # Datasets Coran & Hadiths
│   ├── requirements.txt
│   └── README.md
│
├── frontend/                       # Interface utilisateur
│   └── ...
│
└── README.md
```



## 🛠️ Installation

### Prérequis
- Python 3.10+
- Node.js (pour le frontend)

### Backend

```bash
cd backend

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate    # Windows : venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Lancer le serveur
uvicorn app.main:app --reload --port 8000
```

Le backend sera disponible à l'adresse : `http://localhost:8000`

**Documentation API** : `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## 📌 Utilisation

### Endpoint principal
- **POST** `/chat`
  - `question` : Votre question sur le Coran
  - `mode` : Type de réponse souhaité
  - `user_profile` : Contexte utilisateur (optionnel)

Exemple de réponse :
- Réponse claire et pieuse
- Sources précises (Sourate, Verset, Texte arabe, Traduction)
- Références Hadiths quand pertinent

---

## 🤝 Contribution

Les contributions sont les bienvenues !  
N'hésitez pas à :
1. Forker le projet
2. Créer une branche (`feature/nouvelle-fonctionnalite`)
3. Faire vos modifications
4. Ouvrir une Pull Request

---

## 📄 Licence

Ce projet est distribué sous licence **MIT**. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 🙏 Remerciements

- À la communauté musulmane pour son soutien et ses retours
- Aux contributeurs open-source des outils RAG et des modèles d'embeddings
- À tous ceux qui œuvrent pour rendre la connaissance du Coran plus accessible grâce à l'IA

---

<div align="center">

Made with ❤️ 

</div>
