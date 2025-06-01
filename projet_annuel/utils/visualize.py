import numpy as np
import cv2
from config import classes

colors = [tuple(np.random.randint(0, 255, 3).tolist()) for _ in classes]

def overlay_mask(frame, mask):
    h, w = frame.shape[:2]
    mask = cv2.resize(mask, (w, h), interpolation=cv2.INTER_NEAREST)
    overlay = frame.copy()
    for class_idx, color in enumerate(colors):
        overlay[mask == class_idx] = color
    return overlay