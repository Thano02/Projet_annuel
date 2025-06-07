import os
import shutil
from glob import glob

# Dossier d'entrée
root = "dataset_yolo"
splits = ["train", "val", "test"]

for split in splits:
    print(f"🔄 Réorganisation de {split}...")

    input_dir = os.path.join(root, "images", split)
    output_dir = os.path.join(root, "images", f"{split}_flat")
    os.makedirs(output_dir, exist_ok=True)

    for class_dir in os.listdir(input_dir):
        class_path = os.path.join(input_dir, class_dir)
        if not os.path.isdir(class_path):
            continue

        for file in os.listdir(class_path):
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                src = os.path.join(class_path, file)
                dst = os.path.join(output_dir, file)
                shutil.copy2(src, dst)

    # Supprimer l’ancien dossier structuré
    shutil.rmtree(input_dir)
    os.rename(output_dir, input_dir)

print("✅ Toutes les images ont été aplaties pour chaque split.")
