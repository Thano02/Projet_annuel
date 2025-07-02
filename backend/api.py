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

# === Chargement du modèle YOLO ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model", "yolo_finetune", "final_model", "best.pt")
model = YOLO(MODEL_PATH)

# === Variables ===
current_frame = None
latest_detections = []
frame_queue = queue.Queue()

CAPTURE_DIR = "captured"
CORRECTIONS_FILE = "corrections.csv"
os.makedirs(CAPTURE_DIR, exist_ok=True)

# === Worker de traitement YOLO ===
def yolo_worker():
    global latest_detections
    print("🚀 YOLO worker démarré")
    while True:
        frame = frame_queue.get()
        if frame is None:
            print("⚠️ Frame vide reçue dans le worker")
            frame_queue.task_done()
            continue

        print("📥 Nouvelle frame reçue dans le worker")
        print(f"🖼️ Frame shape : {frame.shape}")
        print("🧪 Envoi au modèle YOLO...")

        try:
            results = model(frame)
        except Exception as e:
            print(f"❌ Erreur YOLO : {e}")
            frame_queue.task_done()
            continue

        detections = []
        height, width, _ = frame.shape
        boxes = results[0].boxes.data.tolist() if results[0].boxes is not None else []
        names = results[0].names if hasattr(results[0], "names") else {}

        print(f"📦 {len(boxes)} box(es) détectée(s)")

        for box in boxes:
            try:
                x1, y1, x2, y2, score, class_id = box
                label = names[int(class_id)] if int(class_id) in names else "inconnu"
                detections.append({
                    "id": str(uuid.uuid4()),
                    "label": label,
                    "score": round(score, 2),
                    "bbox": [int(x1), int(y1), int(x2 - x1), int(y2 - y1)],
                    "image_width": width,
                    "image_height": height
                })
            except Exception as e:
                print(f"❌ Erreur lecture d'une box : {e}")

        latest_detections = detections
        print(f"🔎 Dernières détections : {latest_detections}")
        frame_queue.task_done()

threading.Thread(target=yolo_worker, daemon=True).start()
print("🧵 Thread lancé")

# === Réception de frames ===
@app.post("/upload_frame")
async def upload_frame(file: UploadFile):
    global current_frame
    contents = await file.read()
    print(f"✅ Reçu une frame de {len(contents)} octets")

    nparr = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if frame is None:
        print("❌ Erreur décodage image (cv2.imdecode)")
        return JSONResponse(status_code=400, content={"message": "Erreur décodage image"})

    current_frame = frame
    print(f"🖼️ Frame shape : {frame.shape}")
    print("📨 Frame envoyée dans la file de traitement")
    frame_queue.put(frame)
    return {"status": "ok"}

# === Streaming MJPEG avec box forcée pour test ===
@app.get("/video_feed")
async def video_feed():
    def generate():
        while True:
            if current_frame is not None:
                annotated_frame = current_frame.copy()
                h, w, _ = annotated_frame.shape

                # Bounding box de test (ROUGE)
                x, y, w_box, h_box = int(w * 0.25), int(h * 0.25), int(w * 0.5), int(h * 0.5)
                cv2.rectangle(annotated_frame, (x, y), (x + w_box, y + h_box), (0, 0, 255), 2)
                cv2.putText(annotated_frame, "TEST_BOX", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

                # Dessin des box YOLO (VERT)
                for det in latest_detections:
                    x, y, w, h = det["bbox"]
                    cv2.rectangle(annotated_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(annotated_frame, det["label"], (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                ret, buffer = cv2.imencode('.jpg', annotated_frame)
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            else:
                time.sleep(0.1)

    return StreamingResponse(generate(), media_type="multipart/x-mixed-replace; boundary=frame")

# === Détéctions brutes (pour le front)
@app.get("/detections")
async def get_detections():
    return JSONResponse(content=latest_detections)

# === Correction utilisateur
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
