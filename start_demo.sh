#!/bin/bash

# === Libère les ports ===
kill $(lsof -t -i:8000) 2>/dev/null

# === Lancer le backend FastAPI local ===
(cd backend && uvicorn api:app --host 0.0.0.0 --port 8000 > /dev/null 2>&1) &
PID_BACK=$!

# === Démarrer ngrok ===
ngrok http 8000 > /dev/null &
PID_NGROK=$!

# === Attendre le démarrage de ngrok ===
sleep 5

# === Récupérer l'URL publique ngrok ===
NGROK_URL=$(curl -s http://127.0.0.1:4040/api/tunnels | jq -r '.tunnels[0].public_url')
echo ""
echo "-------------------------------------------------"
echo "Ngrok exposé sur : $NGROK_URL"
echo "-------------------------------------------------"
echo ""

# === Mettre à jour Vercel ===
python update_vercel_env.py "$NGROK_URL"

echo "-------------------------------------------------"
echo "✅ Interface : https://projetannuel.vercel.app"
echo "-------------------------------------------------"

# === Gestion du CTRL+C pour tout arrêter ===
trap "kill $PID_BACK $PID_NGROK; exit 0" SIGINT

wait
