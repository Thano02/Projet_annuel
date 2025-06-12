import os
import pandas as pd
import subprocess

CSV_PATH = "backend/corrections.csv"
THRESHOLD = 100

if not os.path.exists(CSV_PATH):
    print("❌ Fichier corrections.csv introuvable.")
    exit()

df = pd.read_csv(CSV_PATH)
if len(df) < THRESHOLD:
    print(f"⏸ Seulement {len(df)} lignes, seuil de {THRESHOLD} non atteint.")
    exit()

print("✅ Seuil atteint. Lancement du nettoyage et de l'entraînement.")
subprocess.run(["python", "clean_correction.py"], check=True)
subprocess.run(["python", "train_from_corrections.py"], check=True)
