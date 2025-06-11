from ultralytics import YOLO
import cv2

def run_yolo_webcam():
    # Charger le modèle YOLOv8
    model = YOLO("clean_dataset/runs/segment/train/weights/best.pt")  # adapte le chemin si nécessaire

    # Accès à la webcam
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Détection
        results = model(frame)

        # Annoter l'image avec les résultats
        annotated_frame = results[0].plot()

        # Afficher
        cv2.imshow("Détection de déchets - YOLOv8", annotated_frame)

        # Quitter avec la touche 'q'
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_yolo_webcam()
