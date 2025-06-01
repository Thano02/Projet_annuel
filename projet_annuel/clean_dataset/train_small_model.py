from ultralytics import YOLO

# Charger le modèle pré-entraîné YOLOv8 pour segmentation
model = YOLO("yolov8n-seg.pt")  # tu peux changer pour yolov8s-seg.pt si tu veux plus de précision

# Entraîner le modèle sur ton petit dataset annoté (Roboflow exporté)
model.train(
    data="garbage-segmentation.yolov8/data.yaml",  # fichier YAML généré par Roboflow
    epochs=50,
    imgsz=640
)