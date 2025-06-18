FROM python:3.10-slim

WORKDIR /app

# Installer les dépendances système nécessaires à OpenCV
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*

COPY backend/ .

RUN pip install --no-cache-dir --upgrade pip
RUN pip install pandas opencv-python ultralytics fastapi uvicorn tqdm

ENV PYTHONPATH="${PYTHONPATH}:/app"

EXPOSE 8000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
