# === Test du modèle pré-entraîné YOLOv8n-seg sur une image générique ===
from ultralytics import YOLO
from PIL import Image
import matplotlib.pyplot as plt

# Charger le modèle pré-entraîné
model = YOLO("model/yolov8n-seg.pt")
print("\\n=== Test du modèle YOLOv8n-seg pré-entraîné ===")

# Image générique de test (tu peux mettre n'importe quelle image avec objets COCO)
image_path = "dataset_yolo/images/train/biological_20.jpg"

if os.path.exists(image_path):
    try:
        results = model.predict(image_path, imgsz=640, show=False)
        res_plotted = results[0].plot()
        img = Image.fromarray(res_plotted)
        img.show()
        print("✅ Image affichée avec les prédictions du modèle pré-entraîné.")
    except Exception as e:
        print(f"❌ Erreur lors de la prédiction avec le modèle pré-entraîné : {e}")
else:
    print(f"❌ Image introuvable : {image_path}")
