import os
import shutil
from sklearn.model_selection import train_test_split

# Dossier d'origine
source_dir = "C:/Users/ethan/OneDrive/Bureau/garbage-dataset" # Le dossier contenant les 9 catégories
output_dir = "../dataset_yolo"  # Dossier de sortie pour la structure YOLOv8

splits = ['train', 'val', 'test']
split_ratios = [0.7, 0.2, 0.1]réalis

# Parcours de chaque classe
for class_name in os.listdir(source_dir):
    class_path = os.path.join(source_dir, class_name)²²
    if not os.path.isdir(class_path):
        continue

    # Récupère les images
    images = [f for f in os.listdir(class_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

    # Séparation en train/val/test
    train_val, test = train_test_split(images, test_size=split_ratios[2], random_state=42)
    train, val = train_test_split(train_val, test_size=split_ratios[1] / (split_ratios[0] + split_ratios[1]),
                                  random_state=42)

    split_data = {
        'train': train,
        'val': val,
        'test': test
    }

    # Copie des fichiers dans la nouvelle structure
    for split, files in split_data.items():
        dest_dir = os.path.join(output_dir, 'images', split, class_name)
        os.makedirs(dest_dir, exist_ok=True)

        for file in files:
            src_file = os.path.join(class_path, file)
            dst_file = os.path.join(dest_dir, file)
            shutil.copy2(src_file, dst_file)

print("✅ Structure YOLOv8 générée dans 'dataset_yolo/images/' avec train/val/test pour chaque classe.")
