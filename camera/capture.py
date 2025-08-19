import cv2
import numpy as np
import requests
import time
from config import ESP32CAM_CAPTURE_URL, DEBUG


def capture_image():
    # Fetches a single frame from ESP32-CAM /capture endpoint
    # and returns it as an OpenCV (BGR) image.
    try:
        response = requests.get(ESP32CAM_CAPTURE_URL, timeout=5)
        response.raise_for_status()

        img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        if DEBUG:
            filename = f'./{time.strftime("capture_%Y%m%d_%H%M%S.jpg")}'
            with open(filename, "wb") as f:
                f.write(response.content)

        if frame is None:
            raise ValueError("Failed to decode image from ESP32-CAM")

        return frame

    except Exception as e:
        print(f"[ERROR] Could not fetch frame: {e}")
        return None
