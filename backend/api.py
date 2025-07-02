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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model", "yolo_finetune", "final_model", "best.pt")
model = YOLO(MODEL_PATH)

current_frame = None
latest_detections = []
frame_queue = queue.Queue()

CAPTURE_DIR = "captured"
CORRECTIONS_FILE = "corrections.csv"
os.makedirs(CAPTURE_DIR, exist_ok=True)

# === WORKER YOLO ===
def yolo_worker():
    global latest_detections
    print("🚀 YOLO worker démarré")
    while True:
        frame = frame_queue.get()
        try:
            if frame is None:
                print("❌ Frame vide (None)")
                continue

            height, width, _ = frame.shape
            print(f"🖼️ Frame shape : ({height}, {width}, 3)")

            if height < 100 or width < 100:
                print("⚠️ Image trop petite, risque de mauvaise détection")

            print("🔍 Lancement YOLO inference...")
            results = model(frame)
            print("✅ Inférence YOLO terminée")

            boxes_data = getattr(results[0].boxes, "data", None)
            names = getattr(results[0], "names", {})

            if boxes_data is None:
                print("❌ Aucun résultat (boxes_data est None)")
                latest_detections = []
                continue

            print(f"📦 boxes_data type: {type(boxes_data)}, shape: {getattr(boxes_data, 'shape', 'inconnu')}")
            print(f"📦 Contenu brut : {boxes_data}")

            detections = []
            if len(boxes_data) == 0:
                print("🛑 Aucune détection effectuée (tensor vide)")
            else:
                for i, box_tensor in enumerate(boxes_data):
                    try:
                        box = box_tensor.tolist()
                        if len(box) < 6:
                            print(f"⚠️ Box incomplète : {box}")
                            continue
                        x1, y1, x2, y2, score, class_id = box
                        label = names.get(int(class_id), f"class_{int(class_id)}")
                        det = {
                            "id": str(uuid.uuid4()),
                            "label": label,
                            "score": round(score, 2),
                            "bbox": [int(x1), int(y1), int(x2 - x1), int(y2 - y1)],
                            "image_width": width,
                            "image_height": height
                        }
                        detections.append(det)
                        print(f"➡️ Détection {i}: {label} ({score:.2f}) @ [{int(x1)}, {int(y1)}, {int(x2)}, {int(y2)}]")
                    except Exception as e:
                        print(f"❌ Erreur traitement box {i}: {e}")

            latest_detections = detections
            print(f"📊 Détections totales enregistrées : {len(detections)}")

        except Exception as e:
            print(f"❌ Erreur générale YOLO : {e}")
        finally:
            frame_queue.task_done()

threading.Thread(target=yolo_worker, daemon=True).start()
print("🧵 Thread lancé")

@app.post("/upload_frame")
async def upload_frame(file: UploadFile):
    global current_frame
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    current_frame = frame
    print(f"✅ Reçu une frame de {len(contents)} octets")
    print(f"🖼️ Frame shape : {frame.shape}")
    frame_queue.put(frame)
    print("📨 Frame envoyée dans la file de traitement")
    return {"status": "ok"}

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

@app.get("/detections")
async def get_detections():
    return JSONResponse(content=latest_detections)

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
