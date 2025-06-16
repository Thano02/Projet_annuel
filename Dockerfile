# --- Build frontend ---
FROM node:16 AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# --- Prépare Python & backend ---
FROM python:3.9-slim AS backend-base
WORKDIR /app
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# --- Image finale ---
FROM backend-base AS final
WORKDIR /app

# Copie backend
COPY backend/ ./

# Copie les fichiers statiques du frontend
COPY --from=frontend-build /app/frontend/dist ./frontend/dist

# Installe 'serve' pour héberger le statique
RUN pip install uvicorn[standard] && \
    pip install --no-cache-dir serve

# Copie le start.sh et rends-le exécutable
COPY start.sh .
RUN chmod +x start.sh

# Expose les ports
EXPOSE 8000 5173

# Lancement
CMD ["./start.sh"]