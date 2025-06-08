import cv2

print("Appuyez sur 'q' pour fermer une caméra et passer à la suivante.\n")

for i in range(5):
    print(f"Tentative d'ouverture de la caméra à l'index {i}...")
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"Caméra trouvée à l'index {i}.")
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Impossible de lire le flux.")
                break

            cv2.imshow(f"Caméra {i}", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
    else:
        print(f"Pas de caméra à l'index {i}.")
