#!/bin/bash

# Libère les ports si déjà utilisés
kill $(lsof -t -i:8000) 2>/dev/null
kill $(lsof -t -i:5173) 2>/dev/null

# Lance le backend silencieusement
(cd backend && uvicorn api:app --reload > /dev/null 2>&1) &
PID_BACK=$!

# Lance le frontend silencieusement
(cd frontend && npm run dev -- --port 5173 > /dev/null 2>&1) &
PID_FRONT=$!

# Gère CTRL+C pour tuer les deux
trap "kill $PID_BACK $PID_FRONT; exit 0" SIGINT

# Affiche uniquement l'adresse du front
echo "http://localhost:5173"

# Garde le script actif tant que les serveurs tournent
wait
