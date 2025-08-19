import cv2
import numpy as np


def detect_potholes(image, lower_thresh=(0, 0, 0), upper_thresh=(100, 100, 100)):
    """
    Detect potholes in an image using color thresholding.

    Args:
        image (ndarray): Input BGR image (OpenCV format).
        lower_thresh (tuple): Lower BGR threshold for pothole detection.
        upper_thresh (tuple): Upper BGR threshold for pothole detection.

    Returns:
        mask (ndarray): Binary mask (255 = pothole, 0 = non-pothole).
        contours (list): Contours of detected potholes.
    """
    if image is None:
        raise ValueError("Input image is None")

    # Convert to HSV (better for color thresholding)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define threshold ranges (dark colors for potholes)
    lower = np.array(lower_thresh, dtype=np.uint8)
    upper = np.array(upper_thresh, dtype=np.uint8)

    # Apply color threshold
    mask = cv2.inRange(hsv, lower, upper)

    # Morphological operations to reduce noise
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # Find contours of pothole regions
    contours, _ = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    return mask, contours


def draw_potholes(image, contours, color=(0, 0, 255)):
    """
    Draw bounding boxes around detected potholes.

    Args:
        image (ndarray): Input BGR image.
        contours (list): Contours of detected potholes.
        color (tuple): BGR color for bounding boxes.

    Returns:
        ndarray: Image with pothole bounding boxes.
    """
    output = image.copy()
    for cnt in contours:
        if cv2.contourArea(cnt) > 200:  # filter out small noise
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(output, (x, y), (x + w, y + h), color, 2)
    return output
