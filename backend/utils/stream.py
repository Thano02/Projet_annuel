from fastapi import Response
import cv2

cap = cv2.VideoCapture(0)

def generate_frames():
    while True:
        success, frame = cap.read()
        if not success:
            continue
        _, buffer = cv2.imencode(".jpg", frame)
        frame = buffer.tobytes()
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

from fastapi import APIRouter
router = APIRouter()

@router.get("/video_feed")
def video_feed():
    return Response(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")