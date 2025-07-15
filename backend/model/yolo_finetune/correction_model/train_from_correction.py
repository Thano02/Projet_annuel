from ultralytics import YOLO
import os
import shutil
from datetime import datetime

# === CONFIGURATION ===
USE_PREVIOUS_MODEL = False  # Passer à True si on veut fine-tuner sur un modèle précédent
PREVIOUS_MODEL_PATH = "model/yolo_finetune/final_model/weights/best.pt"
BASE_MODEL_PATH = "yolov8n-seg.pt"  # Ou yolov8n.pt si pas de segmentation
MODEL_SAVE_DIR = "model/yolo_finetune/final_model/weights"
DATA_DIR = "corrections_to_train"

# === 1. Choix du modèle de départ ===
model_path = PREVIOUS_MODEL_PATH if USE_PREVIOUS_MODEL else BASE_MODEL_PATH
print(f"📦 Modèle utilisé : {model_path}")

# === 2. Création du fichier data.yaml requis par YOLOv8 ===
data_yaml = f"""
path: {DATA_DIR}
train: images/train
val: images/train
nc: 6
names: ['biological', 'cardboard', 'glass', 'metal', 'paper', 'plastic']
"""

data_yaml_path = os.path.join(DATA_DIR, "data.yaml")
with open(data_yaml_path, "w") as f:
    f.write(data_yaml.strip())

# === 3. Sauvegarde de l’ancien modèle best.pt s’il existe ===
if USE_PREVIOUS_MODEL and os.path.exists(PREVIOUS_MODEL_PATH):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = PREVIOUS_MODEL_PATH.replace("best.pt", f"best_backup_{timestamp}.pt")
    os.makedirs(os.path.dirname(backup_path), exist_ok=True)
    shutil.copy2(PREVIOUS_MODEL_PATH, backup_path)
    print(f"📁 Ancien modèle sauvegardé dans : {backup_path}")

# === 4. Entraînement YOLOv8 ===
model = YOLO(model_path)

result = model.train(
    data=data_yaml_path,
    epochs=30,
    imgsz=640,
    batch=16,
    project="correction_retrain",
    name="from_corrections",
    save=True
)

# === 5. Sauvegarde du nouveau modèle best.pt ===
trained_weights_dir = os.path.join("correction_retrain", "from_corrections", "weights")
new_best_path = os.path.join(trained_weights_dir, "best.pt")

if os.path.exists(new_best_path):
    os.makedirs(MODEL_SAVE_DIR, exist_ok=True)
    shutil.copy2(new_best_path, PREVIOUS_MODEL_PATH)
    print(f"✅ Nouveau modèle sauvegardé dans : {PREVIOUS_MODEL_PATH}")
else:
    print("⚠️ Aucun fichier best.pt trouvé après l'entraînement.")

print("✅ Entraînement terminé.")
