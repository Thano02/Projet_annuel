# Image de base légère
FROM python:3.10-slim

# Crée le dossier de travail
WORKDIR /app

# Copier seulement la partie backend dans le container
COPY backend/ .

# Installer les dépendances nécessaires
RUN pip install --no-cache-dir --upgrade pip
RUN pip install pandas opencv-python ultralytics fastapi uvicorn tqdm

# Ajouter /app au PYTHONPATH pour que uvicorn trouve api.py
ENV PYTHONPATH="${PYTHONPATH}:/app"

# Exposer le port pour Render
EXPOSE 8000

# Commande de lancement
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
