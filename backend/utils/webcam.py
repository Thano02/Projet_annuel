import cv2
import torch
import torchvision.transforms as T
from config import IMG_SIZE, NUM_CLASSES, MODEL_PATH
from model.mini_unet import UNet
from utils.visualize import overlay_mask

def run_webcam():
    model = UNet(num_classes=NUM_CLASSES)
    model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
    model.eval()

    transform = T.Compose([
        T.ToPILImage(),
        T.Resize((IMG_SIZE, IMG_SIZE)),
        T.ToTensor(),
    ])

    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        input_tensor = transform(frame).unsqueeze(0)
        with torch.no_grad():
            output = model(input_tensor)[0]
            mask = torch.argmax(output, dim=0).numpy().astype(np.uint8)

        annotated = overlay_mask(frame, mask)
        cv2.imshow("Mini U-Net Segmentation", annotated)
        if cv2.waitKey(1) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()