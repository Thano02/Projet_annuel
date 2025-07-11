import psycopg2
import subprocess

PG_CONFIG = {
    "host": os.getenv("PGHOST"),
    "port": os.getenv("PGPORT", "5432"),
    "dbname": os.getenv("PGDATABASE"),
    "user": os.getenv("PGUSER"),
    "password": os.getenv("PGPASSWORD")
}

THRESHOLD = 100

try:
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM corrections_user;")
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
