import os
import cv2
import shutil
import psycopg2
import pandas as pd
from tqdm import tqdm
import ast

# === CONFIGURATION ===
PG_HOST = "containers-us-west-157.railway.app"
PG_PORT = "5432"
PG_DB = "railway"
PG_USER = "postgres"
PG_PASSWORD = "WuhubolldZrhJtXlLkeUMpV1ANdiBBqk"

IMAGES_DIR = "captured"
OUTPUT_DIR = "corrections_to_train"
HISTORY_CSV = "backend/historique_corrections.csv"
MIN_CROP_SIZE = 20
VALID_CLASSES = {"biological", "cardboard", "glass", "metal", "paper", "plastic"}

# === 1. Préparation des dossiers YOLO ===
img_out_dir = os.path.join(OUTPUT_DIR, "images", "train")
label_out_dir = os.path.join(OUTPUT_DIR, "labels", "train")
os.makedirs(img_out_dir, exist_ok=True)
os.makedirs(label_out_dir, exist_ok=True)

# === 2. Connexion à PostgreSQL et récupération des corrections ===
def fetch_corrections():
    try:
        conn = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            dbname=PG_DB,
            user=PG_USER,
            password=PG_PASSWORD
        )
        cur = conn.cursor()
        cur.execute("""
            SELECT timestamp, image_filename, crop_filename, bbox,
                   predicted_category, wrong_category, corrected_category, confidence
            FROM corrections
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()

        columns = [
            "timestamp", "image_filename", "crop_filename", "bbox",
            "predicted_category", "wrong_category", "corrected_category", "confidence"
        ]
        return pd.DataFrame(rows, columns=columns)

    except Exception as e:
        print("❌ Erreur PostgreSQL :", e)
        return pd.DataFrame()

df = fetch_corrections()

required_columns = {
    "timestamp", "image_filename", "crop_filename", "bbox",
    "predicted_category", "wrong_category", "corrected_category", "confidence"
}

if df.empty or not required_columns.issubset(df.columns):
    print("❌ Données manquantes ou incomplètes.")
    exit()

valid_entries = []

# === 3. Validation des corrections ===
for _, row in tqdm(df.iterrows(), total=len(df), desc="🔍 Vérification"):
    crop_path = os.path.join(IMAGES_DIR, row["crop_filename"])
    if not os.path.exists(crop_path):
        continue

    try:
        bbox = ast.literal_eval(row["bbox"]) if isinstance(row["bbox"], str) else row["bbox"]
        if len(bbox) != 4:
            continue
        x, y, w, h = map(int, bbox)
        if w < MIN_CROP_SIZE or h < MIN_CROP_SIZE:
            continue
    except:
        continue

    if row["corrected_category"] == row["predicted_category"]:
        continue

    try:
        conf = float(row["confidence"])
        if not (0.0 <= conf <= 1.0):
            continue
    except:
        continue

    img = cv2.imread(crop_path, cv2.IMREAD_GRAYSCALE)
    if img is None or img.shape[0] < MIN_CROP_SIZE or img.shape[1] < MIN_CROP_SIZE:
        continue
    if img.std() < 5:
        continue

    valid_entries.append((row, crop_path, bbox))

print(f"✅ {len(valid_entries)} corrections valides prêtes à être utilisées.")

# === 4. Création des fichiers YOLO ===
class_mapping = {
    "biological": 0,
    "cardboard": 1,
    "glass": 2,
    "metal": 3,
    "paper": 4,
    "plastic": 5
}

for idx, (row, img_path, bbox) in enumerate(valid_entries):
    new_filename = f"cor_{idx:04d}.jpg"
    label_filename = f"cor_{idx:04d}.txt"

    shutil.copy2(img_path, os.path.join(img_out_dir, new_filename))

    x, y, w, h = bbox
    cx = (x + w / 2) / 640
    cy = (y + h / 2) / 640
    nw = w / 640
    nh = h / 640

    class_id = class_mapping.get(row["corrected_category"])
    if class_id is None:
        continue

    with open(os.path.join(label_out_dir, label_filename), "w") as f:
        f.write(f"{class_id} {cx:.6f} {cy:.6f} {nw:.6f} {nh:.6f}\n")

# === 5. Historisation ===
if valid_entries:
    df_valid = pd.DataFrame([row for row, _, _ in valid_entries])

    os.makedirs(os.path.dirname(HISTORY_CSV), exist_ok=True)

    if os.path.exists(HISTORY_CSV):
        df_valid.to_csv(HISTORY_CSV, mode="a", header=False, index=False)
    else:
        df_valid.to_csv(HISTORY_CSV, index=False)

    print(f"📁 {len(valid_entries)} lignes ajoutées à l’historique.")
else:
    print("ℹ️ Aucune donnée valable à historiser.")
