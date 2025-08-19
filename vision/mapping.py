import cv2
import os
from datetime import datetime

def draw_grid(image, grid_size=(40, 25), color=(0, 0, 255)):
    """
    Draws grid lines over an image for visualization.
    """
    overlay = image.copy()
    h, w = image.shape[:2]
    cols, rows = grid_size

    # vertical lines
    for c in range(1, cols):
        x = int(c * w / cols)
        cv2.line(overlay, (x, 0), (x, h), color, 1)

    # horizontal lines
    for r in range(1, rows):
        y = int(r * h / rows)
        cv2.line(overlay, (0, y), (w, y), color, 1)

    return overlay


def save_image_with_grid(input_path, output_dir=".", grid_size=(40, 25), color=(0, 0, 255)):
    """
    Loads an image, converts it to a grid, saves it with a timestamped filename, and returns the output path.
    """
    image = cv2.imread(input_path)
    if image is None:
        raise FileNotFoundError(f"Could not read image: {input_path}")

    image_with_grid = draw_grid(image, grid_size, color)

    # Generate unique filename using current date and time
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"grid_{timestamp}.jpg"

    cv2.imwrite(filename, image_with_grid)
    return filename
