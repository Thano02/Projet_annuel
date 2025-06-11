from ultralytics import YOLO

# Charger le modèle YOLOv8 segmentation pré-entraîné
model = YOLO("yolov8n-seg.pt")

# Lancer l'entraînement sur ton dataset annoté
model.train(
    data="dataset_yolo/data.yaml",
    epochs=50,
    imgsz=640,
    batch=16,
    project="yolo_finetune",
    name="final_model",
    save=True,
    classes=6
)