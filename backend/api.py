from fastapi import FastAPI, UploadFile, Body
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO
import cv2
import numpy as np
import os
import threading
import queue
import time
import uuid
from datetime import datetime
import pandas as pd

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Chargement du modèle YOLO fine-tuné ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model", "yolo_finetune", "final_model", "best.pt")
model = YOLO(MODEL_PATH)

# === Variables globales ===
current_frame = None
latest_detections = []
frame_queue = queue.Queue()

# === Fichiers de correction ===
CAPTURE_DIR = "captured"
CORRECTIONS_FILE = "corrections.csv"
os.makedirs(CAPTURE_DIR, exist_ok=True)

# === Worker YOLO (background thread) ===
def yolo_worker():
    global latest_detections
    print("🚀 YOLO worker démarré")

    while True:
        try:
            frame = frame_queue.get()
            print("📥 Nouvelle frame reçue dans le worker")

            # Shape de l'image
            print(f"🖼️ Frame shape : {frame.shape}")

            # Inférence YOLO
            try:
                print("🧪 Envoi au modèle YOLO...")
                results = model(frame)
                print("✅ Inférence YOLO terminée")
            except Exception as e:
                print(f"❌ Erreur pendant l'inférence YOLO : {e}")
                latest_detections = []
                frame_queue.task_done()
                continue

            detections = []
            height, width, _ = frame.shape
            boxes = results[0].boxes.data.tolist()
            names = results[0].names

            print(f"📦 Nombre de boxes : {len(boxes)}")

            if not boxes:
                print("⚠️ Aucune détection sur cette frame")

            for box in boxes:
                try:
                    x1, y1, x2, y2, score, class_id = box
                    label = names[int(class_id)]
                    detections.append({
                        "id": str(uuid.uuid4()),
                        "label": label,
                        "score": round(score, 2),
                        "bbox": [int(x1), int(y1), int(x2 - x1), int(y2 - y1)],
                        "image_width": width,
                        "image_height": height
                    })
                except Exception as e:
                    print(f"❌ Erreur parsing box : {e}")

            # Fallback debug (désactivé)
            # if not detections:
            #     print("🧪 Insertion box de test")
            #     detections.append({
            #         "id": str(uuid.uuid4()),
            #         "label": "test",
            #         "score": 0.99,
            #         "bbox": [100, 100, 200, 200],
            #         "image_width": width,
            #         "image_height": height
            #     })

            print(f"📊 Détections totales enregistrées : {len(detections)}")
            latest_detections = detections
            frame_queue.task_done()

        except Exception as e:
            print(f"❌ Erreur dans le worker YOLO principal : {e}")

# === Démarrage du thread
threading.Thread(target=yolo_worker, daemon=True).start()
print("🧵 Thread lancé")

# === Upload depuis uploader_local.py
@app.post("/upload_frame")
async def upload_frame(file: UploadFile):
    global current_frame
    contents = await file.read()
    print(f"✅ Reçu une frame de {len(contents)} octets")

    try:
        nparr = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        current_frame = frame
        print(f"🖼️ Frame shape : {frame.shape}")
        frame_queue.put(frame)
        print("📨 Frame envoyée dans la file de traitement")
        return {"status": "ok"}
    except Exception as e:
        print(f"❌ Erreur décodage image : {e}")
        return JSONResponse(status_code=500, content={"message": "Erreur décodage image"})

# === Flux MJPEG vidéo
@app.get("/video_feed")
async def video_feed():
    def generate():
        while True:
            if current_frame is not None:
                annotated_frame = current_frame.copy()
                for det in latest_detections:
                    x, y, w, h = det["bbox"]
                    cv2.rectangle(annotated_frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    cv2.putText(annotated_frame, det["label"], (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                ret, buffer = cv2.imencode('.jpg', annotated_frame)
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            else:
                time.sleep(0.1)
    return StreamingResponse(generate(), media_type="multipart/x-mixed-replace; boundary=frame")

# === Detections vers frontend
@app.get("/detections")
async def get_detections():
    return JSONResponse(content=latest_detections)

# === Correction manuelle
@app.post("/correction")
async def save_correction(data: dict = Body(...)):
    if current_frame is None:
        return JSONResponse(status_code=500, content={"message": "Aucune image disponible"})

    frame = current_frame.copy()
    detection = data["detection"]
    x, y, w, h = detection["bbox"]
    crop = frame[y:y+h, x:x+w]

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    full_img_name = f"capture_{timestamp}.jpg"
    crop_img_name = f"crop_{timestamp}.jpg"
    full_path = os.path.join(CAPTURE_DIR, full_img_name)
    crop_path = os.path.join(CAPTURE_DIR, crop_img_name)

    cv2.imwrite(full_path, frame)
    cv2.imwrite(crop_path, crop)

    correction = {
        "timestamp": datetime.now().isoformat(),
        "image_filename": full_img_name,
        "crop_filename": crop_img_name,
        "bbox": detection["bbox"],
        "predicted_category": detection["label"],
        "wrong_category": data["wrong"],
        "corrected_category": data["corrected"],
        "confidence": detection["score"]
    }

    try:
        df = pd.DataFrame([correction])
        if os.path.exists(CORRECTIONS_FILE):
            df.to_csv(CORRECTIONS_FILE, mode="a", header=False, index=False)
        else:
            df.to_csv(CORRECTIONS_FILE, index=False)
        print("✅ Correction enregistrée :", correction)
    except Exception as e:
        print(f"❌ Erreur CSV : {e}")
        return JSONResponse(status_code=500, content={"message": "Erreur CSV"})

    return JSONResponse(content={"message": "Correction enregistrée", "crop": crop_img_name})
