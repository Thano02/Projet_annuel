from fastapi import FastAPI, UploadFile, Body
from fastapi.responses import StreamingResponse, JSONResponse, Response
from starlette.responses import RedirectResponse
from ultralytics import YOLO
from datetime import datetime
import pandas as pd
import cv2
import numpy as np
import threading
import signal
import contextlib
import os
import uuid
import time
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Modèle YOLO fine-tuné ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model", "yolo_finetune", "final_model", "best.pt")
model = YOLO(MODEL_PATH)

# === Dossiers & fichiers ===
CORRECTIONS_FILE = "corrections.csv"
CAPTURE_DIR = "captured"
os.makedirs(CAPTURE_DIR, exist_ok=True)

# === Variables globales ===
latest_detections = []
current_frame = None

# === Endpoint pour uploader les frames depuis l'uploader local ===
@app.post("/upload_frame")
async def upload_frame(file: UploadFile):
    global current_frame, latest_detections
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    current_frame = frame

    # YOLO inference
    with open(os.devnull, 'w') as fnull:
        with contextlib.redirect_stdout(fnull), contextlib.redirect_stderr(fnull):
            results = model(frame)

    latest_detections.clear()
    height, width, _ = frame.shape
    boxes = results[0].boxes.data.tolist()
    names = results[0].names

    for box in boxes:
        x1, y1, x2, y2, score, class_id = box
        label = names[int(class_id)]
        latest_detections.append({
            "id": str(uuid.uuid4()),
            "label": label,
            "score": round(score, 2),
            "bbox": [int(x1), int(y1), int(x2 - x1), int(y2 - y1)],
            "image_width": width,
            "image_height": height
        })

    return {"status": "ok"}

# === Streaming du flux vidéo depuis le cloud ===
@app.get("/video_feed")
async def video_feed():
    def generate():
        while True:
            if current_frame is not None:
                annotated_frame = current_frame.copy()
                # Dessine les bounding boxes sur l'image
                for det in latest_detections:
                    x, y, w, h = det["bbox"]
                    cv2.rectangle(annotated_frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    cv2.putText(annotated_frame, det["label"], (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

                ret, buffer = cv2.imencode('.jpg', annotated_frame)
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            time.sleep(0.1)
    return StreamingResponse(generate(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/detections")
async def get_detections():
    return JSONResponse(content=latest_detections)

@app.post("/correction")
async def save_correction(data: dict = Body(...)):
    print(f"📩 Correction reçue : {data}")

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
