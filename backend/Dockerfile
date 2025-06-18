# Étape 1 : Image de base
FROM python:3.10-slim

# Étape 2 : Définir le répertoire de travail
WORKDIR /app

# Étape 3 : Copier les fichiers backend
COPY . .

# Étape 4 : Installer les dépendances
RUN pip install --no-cache-dir --upgrade pip
RUN pip install pandas opencv-python ultralytics fastapi uvicorn tqdm

# Étape 5 : Exposer le port utilisé par FastAPI
EXPOSE 8000

# Étape 6 : Démarrage du serveur
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
