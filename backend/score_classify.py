import json
import base64
from ultralytics import YOLO

_model = None

def init():
    """
    Appelé une seule fois au démarrage du container Azure ML.
    On charge ici le modèle enregistré sous le nom 'garbage-classifier' version 1.
    """
    global _model
    # Azure ML montera automatiquement le modèle sous la forme "garbage-classifier:1"
    _model = YOLO("garbage-classifier:1")


def run(raw_request: str) -> str:
    """
    raw_request : chaîne JSON contenant {"data": ["<image_base64>"]}
    On renvoie un JSON {"predicted_label": "...", "score": 0.xx}
    """
    # 1) Parser le JSON d’entrée
    req = json.loads(raw_request)
    img_b64 = req["data"][0]

    # 2) Décoder l’image
    img_bytes = base64.b64decode(img_b64)

    # 3) Faire l’inférence
    results = _model.predict(source=img_bytes, imgsz=320)[0]

    # 4) Extraire la première prédiction (ou renvoyer un fallback)
    if len(results.boxes) > 0:
        cls_idx = int(results.boxes.cls[0])
        label   = results.names[cls_idx]
        score   = float(results.boxes.conf[0])
    else:
        label = "none"
        score = 0.0

    # 5) Retourner le JSON
    return json.dumps({
        "predicted_label": label,
        "score":            score
    })