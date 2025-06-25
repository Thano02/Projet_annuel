from fastapi import FastAPI, UploadFile
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import time

# Initialisation FastAPI
app = FastAPI()

# CORS pour autoriser tout (même si dans full stack Render, plus besoin strictement)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Variable globale pour stocker la dernière frame
current_frame = None

# Endpoint de réception des frames
@app.post("/upload_frame")
async def upload_frame(file: UploadFile):
    global current_frame
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    current_frame = frame
    print(f"✅ Reçu une frame de {len(contents)} octets")
    return {"status": "ok"}

# Endpoint du flux MJPEG
@app.get("/video_feed")
async def video_feed():
    def generate():
        while True:
            if current_frame is not None:
                ret, buffer = cv2.imencode('.jpg', current_frame)
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            else:
                time.sleep(0.1)
    return StreamingResponse(generate(), media_type="multipart/x-mixed-replace; boundary=frame")
