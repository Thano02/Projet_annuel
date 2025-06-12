from ultralytics import YOLO
import os
import shutil
from datetime import datetime

# === CONFIGURATION ===
USE_PREVIOUS_MODEL = False  # On passera à True quand on aura assez d'historique pour en mettre dans l'entrainement
PREVIOUS_MODEL_PATH = "model/yolo_finetune/final_model/weights/best.pt"
BASE_MODEL_PATH = "yolov8n-seg.pt"
MODEL_SAVE_DIR = "model/yolo_finetune/final_model/weights"

# === Sélection du modèle ===
model_path = PREVIOUS_MODEL_PATH if USE_PREVIOUS_MODEL else BASE_MODEL_PATH
print(f"📦 Modèle utilisé : {model_path}")

# === Fichier data.yaml pour YOLOv8 ===
data_yaml = """
path: corrections_to_train
train: images/train
val: images/train
nc: 6
names: ['biological', 'cardboard', 'glass', 'metal', 'paper', 'plastic']
"""
with open("corrections_to_train/data.yaml", "w") as f:
    f.write(data_yaml)

# === Sauvegarde de l’ancien best.pt si existant ===
if os.path.exists(PREVIOUS_MODEL_PATH):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = PREVIOUS_MODEL_PATH.replace("best.pt", f"best_backup_{timestamp}.pt")
    os.makedirs(os.path.dirname(backup_path), exist_ok=True)
    shutil.copy2(PREVIOUS_MODEL_PATH, backup_path)
    print(f"📁 Ancien modèle sauvegardé dans : {backup_path}")

# === Lancement de l'entraînement ===
model = YOLO(model_path)
result = model.train(
    data="corrections_to_train/data.yaml",
    epochs=30,
    imgsz=640,
    batch=16,
    project="correction_retrain",
    name="from_corrections",
    save=True
)

# === Recherche du nouveau best.pt ===
trained_weights_dir = os.path.join("correction_retrain", "from_corrections", "weights")
new_best_path = os.path.join(trained_weights_dir, "best.pt")

if os.path.exists(new_best_path):
    os.makedirs(MODEL_SAVE_DIR, exist_ok=True)
    shutil.copy2(new_best_path, PREVIOUS_MODEL_PATH)
    print(f"✅ Nouveau modèle sauvegardé dans : {PREVIOUS_MODEL_PATH}")
else:
    print("⚠️ Aucun fichier best.pt trouvé après l'entraînement.")

print("✅ Entraînement terminé.")
