import os
import cv2
import pandas as pd
import shutil
from tqdm import tqdm

# === CONFIGURATION ===
CORRECTIONS_CSV = "backend/corrections.csv"
HISTORY_CSV = "backend/historique_corrections.csv"
IMAGES_DIR = "captured"
OUTPUT_DIR = "corrections_to_train"
MIN_CROP_SIZE = 20
VALID_CLASSES = {"biological", "cardboard", "glass", "metal", "paper", "plastic"}

# === 1. Préparation du dossier de sortie YOLO ===
img_out_dir = os.path.join(OUTPUT_DIR, "images", "train")
label_out_dir = os.path.join(OUTPUT_DIR, "labels", "train")
os.makedirs(img_out_dir, exist_ok=True)
os.makedirs(label_out_dir, exist_ok=True)

# === 2. Chargement du fichier de corrections ===
try:
    df = pd.read_csv(CORRECTIONS_CSV)
except Exception as e:
    print("❌ Impossible de lire le fichier de corrections :", e)
    exit()

required_columns = {
    "timestamp", "image_filename", "crop_filename", "bbox",
    "predicted_category", "wrong_category", "corrected_category", "confidence"
}

if not required_columns.issubset(df.columns):
    print("❌ Le CSV ne contient pas tous les champs requis.")
    exit()

valid_entries = []

# === 3. Validation et nettoyage des données ===
for _, row in tqdm(df.iterrows(), total=len(df), desc="🔍 Vérification"):
    crop_path = os.path.join(IMAGES_DIR, row["crop_filename"])
    if not os.path.exists(crop_path):
        continue

    try:
        bbox = eval(row["bbox"]) if isinstance(row["bbox"], str) else row["bbox"]
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

# === 4. Création des fichiers images/labels YOLO ===
for idx, (row, img_path, bbox) in enumerate(valid_entries):
    new_filename = f"cor_{idx:04d}.jpg"
    label_filename = f"cor_{idx:04d}.txt"

    shutil.copy2(img_path, os.path.join(img_out_dir, new_filename))

    x, y, w, h = bbox
    cx = (x + w / 2) / 640
    cy = (y + h / 2) / 640
    nw = w / 640
    nh = h / 640

    class_mapping = {
        "biological": 0,
        "cardboard": 1,
        "glass": 2,
        "metal": 3,
        "paper": 4,
        "plastic": 5
    }

    class_id = class_mapping.get(row["corrected_category"])
    if class_id is None:
        continue

    with open(os.path.join(label_out_dir, label_filename), "w") as f:
        f.write(f"{class_id} {cx:.6f} {cy:.6f} {nw:.6f} {nh:.6f}\n")

# === 5. Historisation et vidage du CSV original ===
if valid_entries:
    df_valid = pd.DataFrame([row for row, _, _ in valid_entries])

    # Enregistrement dans l'historique, ici soit on crée le fichier d'historique des corrections, soit on ajoute les nouvelles correction dans le fichier d'historique en mode append
    if os.path.exists(HISTORY_CSV):
        df_valid.to_csv(HISTORY_CSV, mode="a", header=False, index=False)
    else:
        df_valid.to_csv(HISTORY_CSV, index=False)

    # Ajout futur : mélanger avec 20-30% de l’historique quand le fichier existera pour ne pas qu'il soit trop spécialisé dans les nouvelles erreurs seulement
    # df_hist = pd.read_csv(HISTORY_CSV)
    # df_sample = df_hist.sample(frac=0.3, random_state=42)
    # df_valid = pd.concat([df_valid, df_sample], ignore_index=True)

    # Vidage du fichier original pour recevoir de nouvelles corrections
    with open(CORRECTIONS_CSV, "w") as f:
        f.write(",".join(df.columns) + "\n")

    print(f"📁 {len(valid_entries)} lignes ajoutées à l’historique.")
    print("🧹 Fichier corrections.csv vidé pour recevoir de nouvelles entrées.")
else:
    print("ℹ️ Aucune donnée valable. Aucun fichier modifié.")
