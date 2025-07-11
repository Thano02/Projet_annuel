FROM python:3.10-slim

WORKDIR /app

# Installer les dépendances système nécessaires à OpenCV
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*

# Copier tout le code (depuis la racine du repo)
COPY . .

# Mettre à jour pip
RUN pip install --no-cache-dir --upgrade pip

# Installer toutes les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Configurer le PYTHONPATH
ENV PYTHONPATH="${PYTHONPATH}:/app/backend"

EXPOSE 8000

# Lancer l'application
CMD ["uvicorn", "backend.api:app", "--host", "0.0.0.0", "--port", "8000"]
