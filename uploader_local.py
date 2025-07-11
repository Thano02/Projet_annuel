import cv2
import requests
import time

BACKEND_URL = "https://turkey-adjusted-namely.ngrok-free.app"
FRONTEND_URL = "https://interface-projet-annuel.onrender.com"
UPLOAD_ENDPOINT = f"{BACKEND_URL}/upload_frame"
DETECTIONS_ENDPOINT = f"{BACKEND_URL}/detections"
CAMERA_INDEX = 0

def open_camera(index, retries=5, delay=2):
    for attempt in range(retries):
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            print("Caméra détectée")
            return cap
        print(f"Tentative {attempt+1} échec, on réessaie...")
        time.sleep(delay)
    print("Impossible d'accéder à la caméra")
    exit()

cap = open_camera(CAMERA_INDEX)

print("Streaming vers le cloud... (CTRL+C pour arrêter)")

backend_ready = False

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Impossible de lire une frame")
            break

        frame_resized = cv2.resize(frame, (640, 480))
        _, img_encoded = cv2.imencode('.jpg', frame_resized)

        try:
            response = requests.post(
                UPLOAD_ENDPOINT,
                files={"file": ("frame.jpg", img_encoded.tobytes(), "image/jpeg")},
                timeout=20
            )
            if response.status_code == 200 and not backend_ready:
                # Vérification que le backend Render est bien prêt
                for _ in range(10):
                    try:
                        ping = requests.get(DETECTIONS_ENDPOINT, timeout=5)
                        if ping.ok:
                            print(f"Interface accessible ici : {FRONTEND_URL}")
                            backend_ready = True
                            break
                    except:
                        pass
                    time.sleep(1)
        except requests.exceptions.RequestException as e:
            print("Erreur réseau:", e)

        time.sleep(0.5)
except KeyboardInterrupt:
    print("Arrêt manuel")
finally:
    cap.release()
