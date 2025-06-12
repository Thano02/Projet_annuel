from fastapi import FastAPI, Body
from fastapi.responses import StreamingResponse, JSONResponse, Response
from ultralytics import YOLO
from datetime import datetime
import pandas as pd
import cv2
import threading
import signal
import contextlib
import os
import uuid
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
model = YOLO("clean_dataset/runs/segment/train/weights/best.pt")

# === Caméra ===
cap = cv2.VideoCapture(0)
stop_stream = threading.Event()
latest_detections = []

# === Dossiers & fichiers ===
CORRECTIONS_FILE = "corrections.csv"
CAPTURE_DIR = "captured"
os.makedirs(CAPTURE_DIR, exist_ok=True)

# === Gestion propre de l'arrêt ===
def handle_exit(sig, frame):
    print("🛑 Arrêt demandé...")
    stop_stream.set()
    cap.release()

signal.signal(signal.SIGINT, handle_exit)

# === Générateur de frames avec détection YOLO ===
def gen_frames():
    global latest_detections
    while not stop_stream.is_set():
        success, frame = cap.read()
        if not success:
            break

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

        annotated = results[0].plot()
        _, buffer = cv2.imencode('.jpg', annotated)
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

# === Endpoints ===
@app.get("/video_feed")
async def video_feed():
    return StreamingResponse(gen_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/detections")
async def get_detections():
    return JSONResponse(content=latest_detections)

@app.get("/snapshot")
def snapshot():
    success, frame = cap.read()
    if not success:
        return Response(status_code=500)
    _, buffer = cv2.imencode('.jpg', frame)
    return Response(content=buffer.tobytes(), media_type="image/jpeg")

@app.post("/correction")
async def save_correction(data: dict = Body(...)):
    print(f"📩 Correction reçue : {data}")

    # Capture image depuis la caméra
    ret, frame = cap.read()
    if not ret:
        return JSONResponse(status_code=500, content={"message": "Erreur lors de la capture caméra"})

    # Récupération directe de la détection (plus d'ID à rechercher)
    detection = data["detection"]
    x, y, w, h = detection["bbox"]
    crop = frame[y:y+h, x:x+w]

    # Sauvegarde des fichiers
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    full_img_name = f"capture_{timestamp}.jpg"
    crop_img_name = f"crop_{timestamp}.jpg"
    full_path = os.path.join(CAPTURE_DIR, full_img_name)
    crop_path = os.path.join(CAPTURE_DIR, crop_img_name)

    cv2.imwrite(full_path, frame)
    cv2.imwrite(crop_path, crop)

    # Construction de la ligne de correction
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
