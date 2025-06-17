import json
import base64
from ultralytics import YOLO

_model = None

def init():
    """
    Chargement du modèle d’annotation enregistré sous 'garbage-annotator' version 1.
    """
    global _model
    _model = YOLO("garbage-annotator:1")


def run(raw_request: str) -> str:
    """
    raw_request : chaîne JSON contenant {"data": ["<image_base64>"]}
    On renvoie un JSON {"annotations": [ {label, score}, … ]}
    """
    # 1) Parser l’entrée
    req = json.loads(raw_request)
    img_b64 = req["data"][0]

    # 2) Décoder l’image
    img_bytes = base64.b64decode(img_b64)

    # 3) Inférence
    results = _model.predict(source=img_bytes, imgsz=320)[0]

    # 4) Construire la liste d’annotations
    annotations = []
    for cls_idx, conf in zip(results.boxes.cls, results.boxes.conf):
        annotations.append({
            "label": results.names[int(cls_idx)],
            "score": float(conf)
        })

    # 5) Retourner le JSON
    return json.dumps({"annotations": annotations})