from ultralytics import YOLO
import os
import shutil

# === Paramètres ===
model_path = "runs/segment/train/weights/best.pt"  # le modèle entrainé
dataset_root = "dataset_yolo"
splits = ["train", "val"]

# === Charger le modèle YOLOv8 ===
model = YOLO(model_path)

for split in splits:
    img_dir = os.path.join(dataset_root, "images", split)
    label_dir = os.path.join(dataset_root, "labels", split)
    os.makedirs(label_dir, exist_ok=True)

    print(f"🔎 Prédiction sur: {img_dir} ...")

    # Prédiction avec sauvegarde des .txt
    results = model.predict(
        source=img_dir,
        save_txt=True,
        save_conf=True,
        save=False,  # pas besoin d'images annotées ici
        project=os.path.join("runs", "auto_annotate"),
        name=split,
        exist_ok=True
    )

    # Récupérer les .txt générés
    pred_labels_dir = os.path.join("runs", "auto_annotate", split, "labels")
    for file in os.listdir(pred_labels_dir):
        if file.endswith(".txt"):
            shutil.copy2(os.path.join(pred_labels_dir, file), os.path.join(label_dir, file))

    print(f"✅ Annotations sauvegardées dans {label_dir}")

print("🎉 Auto-annotation terminée pour tous les splits !")
