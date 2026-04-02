# Utiliser une image Python legere
FROM python:3.11-slim

# Definir le repertoire de travail
WORKDIR /app

# Empecher Python de generer des fichiers .pyc et forcer l'affichage des logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Installer les dependances systeme necessaires
RUN apt-get update && apt-get install -y --index-url https://pypi.org/simple \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de dependances
COPY requirements.txt .

# Installer les dependances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY . .

# Exposer le port par defaut de FastAPI
EXPOSE 8000

# Utiliser Gunicorn pour la production (avec workers Uvicorn)
# Le port est injecte dynamiquement par Railway via la variable $PORT
CMD ["sh", "-c", "gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:${PORT:-8000} --timeout 120"]
