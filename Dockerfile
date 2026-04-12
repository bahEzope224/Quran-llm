# Image Python robuste et complète
FROM python:3.11-bookworm

# Répertoire de travail dans le conteneur
WORKDIR /app

# Optimisations Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV DEBIAN_FRONTEND=noninteractive

# Dépendances système (compilation et bibliothèques standard)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    libssl-dev \
    zlib1g-dev \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/lib/apt/lists/*

# Copie des dépendances depuis /backend
COPY backend/requirements.txt .

# Installation des dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copie de tout le dossier backend dans /app
COPY backend/ .

# Port dynamique (Railway)
EXPOSE 8000

# Lancement avec Gunicorn
CMD ["sh", "-c", "gunicorn -w 2 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:${PORT:-8000} --timeout 120"]
