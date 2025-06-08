from ultralytics import YOLO
import cv2
import uuid

model = YOLO("clean_dataset/runs/yolov8n-seg.pt")

# Liste partagée pour stocker les dernières détections
latest_detections = []

def get_latest_detections():
    return latest_detections

def detect_and_annotate(frame):
    global latest_detections
    latest_detections.clear()

    results = model(frame)[0]
    boxes = results.boxes.data.tolist()
    names = results.names

    height, width, _ = frame.shape

    for box in boxes:
        x1, y1, x2, y2, score, class_id = box
        label = names[int(class_id)]
        detection_id = str(uuid.uuid4())

        latest_detections.append({
            "id": detection_id,
            "label": label,
            "score": round(score, 2),
            "bbox": [
                int(x1), int(y1),
                int(x2 - x1),
                int(y2 - y1)
            ],
            "image_width": width,
            "image_height": height
        })

    # Annotated frame
    return results.plot()
