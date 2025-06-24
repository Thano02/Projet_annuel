import requests
import sys

# === Credentials Vercel ===
VERCEL_TOKEN = "CXSPNzTRVZUgM77Z2u5dTbYF"
PROJECT_ID = "prj_6we4NVVIhSe13RIeZNMQuPXoHW34"
PROJECT_NAME = "projetannuel"  # Le nom exact de ton projet Vercel

ENV_NAME = "NEXT_PUBLIC_API_URL"
new_value = sys.argv[1]

headers = {
    "Authorization": f"Bearer {VERCEL_TOKEN}",
    "Content-Type": "application/json"
}

# 1️⃣ Liste des variables pour récupérer l'ID
list_url = f"https://api.vercel.com/v10/projects/{PROJECT_ID}/env"
resp_list = requests.get(list_url, headers=headers)
if resp_list.status_code != 200:
    print("❌ Erreur récupération des variables :", resp_list.text)
    sys.exit(1)

envs = resp_list.json()["envs"]
env_id = None
for env in envs:
    if env["key"] == ENV_NAME:
        env_id = env["id"]
        break

if not env_id:
    print("❌ Variable d'environnement non trouvée sur le projet Vercel.")
    sys.exit(1)

# 2️⃣ Mettre à jour la variable d'environnement
update_url = f"https://api.vercel.com/v10/projects/{PROJECT_ID}/env/{env_id}"

payload = {
    "value": new_value,
    "target": ["production", "preview", "development"]
}

resp_update = requests.patch(update_url, headers=headers, json=payload)
if resp_update.status_code != 200:
    print("❌ Erreur mise à jour de la variable :", resp_update.text)
    sys.exit(1)
else:
    print(f"✅ Variable {ENV_NAME} mise à jour avec succès !")

# 3️⃣ Lancer un redeploy automatique propre via integration endpoint
redeploy_url = f"https://api.vercel.com/v1/projects/{PROJECT_NAME}/deployments"
resp_redeploy = requests.post(redeploy_url, headers=headers)

if resp_redeploy.status_code != 201:
    print("❌ Erreur redeploiement :", resp_redeploy.text)
    sys.exit(1)
else:
    print("🚀 Redeploiement Vercel déclenché avec succès !")
