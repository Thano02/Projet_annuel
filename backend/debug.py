
from ultralytics import YOLO
import cv2
import os
from PIL import Image, ImageDraw

# === CONFIGURATION ===
MODELS = {
    "Fine-tuné": "clean_dataset/runs/segment/train/weights/best.pt",
    "Pré-entraîné": "yolov8n-seg.pt"
}
TEST_IMAGE = "dataset_yolo/images/val/biological_58.jpg"
IMG_SIZE = 640

for name, model_path in MODELS.items():
    print(f"\n=== Test avec le modèle : {name} ===")
    try:
        model = YOLO(model_path)
        print("✅ Modèle chargé avec succès.")
    except Exception as e:
        print(f"❌ Erreur de chargement du modèle : {e}")
        continue

    # === Test prédiction sur image ===
    if os.path.exists(TEST_IMAGE):
        try:
            results = model.predict(TEST_IMAGE, imgsz=IMG_SIZE, task="segment", show=False)
            res_plotted = results[0].plot()
            img = Image.fromarray(res_plotted)
            img.show(title=f"Prédictions - {name}")
            if results[0].masks is not None and len(results[0].boxes.cls) > 0:
                print(f"✅ Détections sur l'image test : {len(results[0].boxes.cls)} objets détectés.")
            else:
                print("⚠️ Aucune détection sur l'image test.")
        except Exception as e:
            print(f"❌ Erreur de prédiction sur image : {e}")
    else:
        print(f"❌ Image de test introuvable : {TEST_IMAGE}")

    # === Test prédiction webcam ===
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise ValueError("Impossible d'ouvrir la webcam.")

        ret, frame = cap.read()
        if ret:
            frame = cv2.resize(frame, (IMG_SIZE, IMG_SIZE))
            results = model.predict(source=frame, imgsz=IMG_SIZE, task="segment", show=False)
            res_webcam = results[0].plot()
            cv2.imshow(f"Webcam - {name}", res_webcam)
            cv2.waitKey(3000)
            cv2.destroyAllWindows()
            if results[0].masks is not None and len(results[0].boxes.cls) > 0:
                print(f"✅ Détections sur la webcam : {len(results[0].boxes.cls)} objets détectés.")
            else:
                print("⚠️ Aucune détection en webcam.")
        else:
            print("❌ Impossible de lire une image depuis la webcam.")
        cap.release()
    except Exception as e:
        print(f"❌ Erreur de prédiction webcam : {e}")

# === Vérification rapide des labels ===
LABEL_DIR = "dataset_yolo/labels/train"
try:
    issues_found = 0
    for file in os.listdir(LABEL_DIR):
        if file.endswith(".txt"):
            with open(os.path.join(LABEL_DIR, file), "r") as f:
                lines = f.readlines()
                for line in lines:
                    parts = line.strip().split()
                    if not parts or not parts[0].isdigit():
                        issues_found += 1
                    class_id = int(parts[0])
                    if class_id < 0 or class_id > 5:
                        issues_found += 1
    if issues_found == 0:
        print("✅ Labels de train valides (classes 0 à 5 uniquement).")
    else:
        print(f"⚠️ Problèmes détectés dans les labels : {issues_found} lignes incorrectes.")
except Exception as e:
    print(f"❌ Erreur lors de la vérification des labels : {e}")

# === Visualisation d'une image avec ses labels YOLO ===
print("\n=== Visualisation des annotations sur une image ===")
sample_image = "dataset_yolo/images/train/biological_52.jpg"
sample_label = "dataset_yolo/labels/train/biological_52.txt"

if os.path.exists(sample_image) and os.path.exists(sample_label):
    try:
        img = Image.open(sample_image)
        draw = ImageDraw.Draw(img)
        w, h = img.size

        with open(sample_label, "r") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) != 5:
                    continue
                cls, x, y, bw, bh = map(float, parts)
                x1 = (x - bw / 2) * w
                y1 = (y - bh / 2) * h
                x2 = (x + bw / 2) * w
                y2 = (y + bh / 2) * h
                draw.rectangle([x1, y1, x2, y2], outline="red", width=2)
                draw.text((x1, y1 - 10), f"Classe {int(cls)}", fill="red")

        img.show(title="Image + Labels YOLO")
        print("✅ Image affichée avec les bounding boxes.")
    except Exception as e:
        print(f"❌ Erreur lors de l'affichage : {e}")
else:
    print("❌ Image ou label non trouvé. Modifie le chemin pour tester un autre exemple.")
