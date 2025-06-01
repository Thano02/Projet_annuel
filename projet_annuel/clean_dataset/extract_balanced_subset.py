import os
import shutil
import random
from collections import defaultdict

# Paramètres
base_source = "dataset_yolo/images"
base_output = "dataset_yolo_small/images"
splits = ["train", "val"]
images_per_class = 40  # par split

for split in splits:
    source_dir = os.path.join(base_source, split)
    output_dir = os.path.join(base_output, split)
    os.makedirs(output_dir, exist_ok=True)

    # Récupérer les images par classe (en supposant class_name_*.jpg)
    class_images = defaultdict(list)
    for filename in os.listdir(source_dir):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            class_name = filename.split('_')[0]
            class_images[class_name].append(filename)

    # Sélectionner des images aléatoires par classe
    for class_name, files in class_images.items():
        selected = random.sample(files, min(images_per_class, len(files)))
        for fname in selected:
            src = os.path.join(source_dir, fname)
            dst = os.path.join(output_dir, fname)
            shutil.copy2(src, dst)

print("✅ Sous-dataset équilibré extrait depuis train + val vers dataset_yolo_small/")
