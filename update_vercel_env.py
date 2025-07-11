import json
import requests
import subprocess

def get_ngrok_url():
    try:
        tunnels = requests.get("http://localhost:4040/api/tunnels").json()
        for tunnel in tunnels["tunnels"]:
            if tunnel["proto"] == "https":
                return tunnel["public_url"]
    except Exception as e:
        print("Erreur récupération ngrok:", e)
    return None

def write_config_file(api_url: str):
    config = {
        "API_URL": api_url
    }
    with open("public/config.json", "w") as f:
        json.dump(config, f)
    print("✅ config.json mis à jour avec :", api_url)

if __name__ == "__main__":
    ngrok_url = get_ngrok_url()
    if ngrok_url is None:
        print("Aucun tunnel ngrok trouvé.")
    else:
        backend_url = f"{ngrok_url}"
        write_config_file(backend_url)
