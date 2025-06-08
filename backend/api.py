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

model = YOLO("clean_dataset/runs/yolov8n-seg.pt")

cap = cv2.VideoCapture(0)
stop_stream = threading.Event()
latest_detections = []

CORRECTIONS_FILE = "corrections.csv"
CAPTURE_DIR = "captured"
os.makedirs(CAPTURE_DIR, exist_ok=True)

# Gestion CTRL+C
def handle_exit(sig, frame):
    print("🛑 Arrêt demandé...")
    stop_stream.set()
    cap.release()

signal.signal(signal.SIGINT, handle_exit)

# Génère les frames annotées par YOLO
def gen_frames():
    global latest_detections
    while not stop_stream.is_set():
        success, frame = cap.read()
        if not success:
            break

        # Exécution YOLO sans logs
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

    # Capture caméra au moment de la validation
    ret, frame = cap.read()
    if not ret:
        print("❌ Erreur lors de la capture caméra.")
        return JSONResponse(status_code=500, content={"message": "Erreur lors de la capture caméra"})

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"capture_{timestamp}.jpg"
    filepath = os.path.join(CAPTURE_DIR, filename)

    if not cv2.imwrite(filepath, frame):
        print("❌ Échec d'enregistrement de l'image.")
        return JSONResponse(status_code=500, content={"message": "Erreur enregistrement image"})

    # Enregistrement dans le CSV
    correction = {
        "timestamp": datetime.now().isoformat(),
        "image_filename": filename,
        "wrong_category": data["wrong"],
        "corrected_category": data["corrected"]
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

    return JSONResponse(content={"message": "Correction enregistrée", "filename": filename})
