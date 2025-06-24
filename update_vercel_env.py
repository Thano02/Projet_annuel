import requests
import sys

# === Credentials Vercel ===
VERCEL_TOKEN = "CXSPNzTRVZUgM77Z2u5dTbYF"
PROJECT_ID = "prj_6we4NVVIhSe13RIeZNMQuPXoHW34"

# === Webhook URL officiel Vercel généré ===
DEPLOY_HOOK_URL = "https://api.vercel.com/v1/integrations/deploy/prj_6we4NVVIhSe13RIeZNMQuPXoHW34/uzR3q3GPou"

ENV_NAME = "NEXT_PUBLIC_API_URL"
new_value = sys.argv[1]

headers = {
    "Authorization": f"Bearer {VERCEL_TOKEN}",
    "Content-Type": "application/json"
}

# 1️⃣ Lister les variables existantes pour récupérer l'ID
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

# 3️⃣ Appel du webhook de redeploiement automatique
resp_hook = requests.post(DEPLOY_HOOK_URL)
if resp_hook.status_code != 200:
    print("❌ Erreur déclenchement redeploy via webhook :", resp_hook.text)
    sys.exit(1)
else:
    print("🚀 Redeploiement Vercel déclenché avec succès via webhook !")
