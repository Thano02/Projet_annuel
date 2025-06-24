import requests
import sys

VERCEL_TOKEN = "CXSPNzTRVZUgM77Z2u5dTbYF"
PROJECT_ID = "prj_6we4NVVIhSe13RIeZNMQuPXoHW34"
DEPLOY_HOOK_URL = "https://api.vercel.com/v1/integrations/deploy/prj_6we4NVVIhSe13RIeZNMQuPXoHW34/uzR3q3GPou"

ENV_NAME = "NEXT_PUBLIC_API_URL"
new_value = sys.argv[1]

headers = {
    "Authorization": f"Bearer {VERCEL_TOKEN}",
    "Content-Type": "application/json"
}

# Lister et récupérer l'ID
list_url = f"https://api.vercel.com/v10/projects/{PROJECT_ID}/env"
resp_list = requests.get(list_url, headers=headers)
envs = resp_list.json()["envs"]
env_id = next((env["id"] for env in envs if env["key"] == ENV_NAME), None)

if not env_id:
    print("❌ Variable non trouvée sur Vercel")
    sys.exit(1)

# Mise à jour de la variable
update_url = f"https://api.vercel.com/v10/projects/{PROJECT_ID}/env/{env_id}"
payload = {"value": new_value, "target": ["production", "preview", "development"]}
resp_update = requests.patch(update_url, headers=headers, json=payload)
if resp_update.status_code != 200:
    print("❌ Erreur update variable :", resp_update.text)
    sys.exit(1)
else:
    print("✅ Variable d’environnement mise à jour.")

# Appel du webhook
resp_hook = requests.post(DEPLOY_HOOK_URL)
if resp_hook.status_code not in [200, 202]:
    print("❌ Erreur webhook :", resp_hook.text)
else:
    print("🚀 Redeploiement Vercel lancé.")
