import psycopg2
import subprocess

PG_CONFIG = {
    "host": "containers-us-west-157.railway.app",
    "port": "5432",
    "dbname": "railway",
    "user": "postgres",
    "password": "WuhubolldZrhJtXlLkeUMpV1ANdiBBqk"
}

THRESHOLD = 100

try:
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM corrections;")
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
except Exception as e:
    print("❌ Connexion PostgreSQL échouée :", e)
    exit()

if count < THRESHOLD:
    print(f"⏸ {count} corrections — seuil {THRESHOLD} non atteint.")
    exit()

print("✅ Seuil atteint. Entraînement lancé.")
subprocess.run(["python", "clean_correction.py"], check=True)
subprocess.run(["python", "train_from_corrections.py"], check=True)
