from ultralytics import YOLO

# Charger un modèle pré-entraîné YOLOv8 Segmentation (nano, small, medium, etc.)
model = YOLO("yolov8n-seg.pt")

# Lancer l'entraînement
model.train(
    data="dataset_yolo/data.yaml",
    epochs=50,
    imgsz=640,
    batch=16,
    project="yolo_training",
    name="final_model",
    save=True
)