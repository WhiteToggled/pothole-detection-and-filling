import cv2
import numpy as np
from datetime import datetime
import os

def deduct_pothole(input_path, grid_size=(40, 25), output_dir="."):
    # Load image
    image = cv2.imread(input_path)
    if image is None:
        raise FileNotFoundError(f"Could not read image: {input_path}")
    overlay = image.copy()
    
    h, w = image.shape[:2]
    cell_w = w / grid_size[0]
    cell_h = h / grid_size[1]

    # Convert to HSV for better color detection
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define brownish color range (adjust if needed)
    lower_brown = np.array([10, 50, 50])
    upper_brown = np.array([30, 255, 200])
    mask = cv2.inRange(hsv, lower_brown, upper_brown)

    # Loop over grid cells
    for row in range(grid_size[1]):
        for col in range(grid_size[0]):
            x_start = int(col * cell_w)
            y_start = int(row * cell_h)
            x_end = int((col + 1) * cell_w)
            y_end = int((row + 1) * cell_h)

            # Check if the cell contains brown pixels
            cell_mask = mask[y_start:y_end, x_start:x_end]
            if cv2.countNonZero(cell_mask) > 450:  # threshold, adjust as needed
                cv2.rectangle(overlay, (x_start, y_start), (x_end, y_end), (0, 255, 0), 2)

    # Save image with timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"cordinates{timestamp}.jpg"
    output_path = os.path.join(output_dir, filename)
    cv2.imwrite(output_path, overlay)

    return output_path

