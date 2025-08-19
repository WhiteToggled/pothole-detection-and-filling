import cv2


def pixel_to_grid(pixel_coords, image_size=(500, 500), grid_size=(10, 10)):
    if pixel_coords is None:
        return None

    img_w, img_h = image_size
    grid_w, grid_h = grid_size

    # flatten if nested (e.g. [[333, 4]] → [333, 4])
    if hasattr(pixel_coords, "ndim") and pixel_coords.ndim > 1:
        pixel_coords = pixel_coords[0]

    if isinstance(pixel_coords[0], (list, tuple)):
        pixel_coords = pixel_coords[0]

    px, py = map(int, pixel_coords)

    col = int((px / img_w) * grid_w)
    row = int((py / img_h) * grid_h)

    col = max(0, min(col, grid_w - 1))
    row = max(0, min(row, grid_h - 1))

    return (col, row)




def draw_grid(image, grid_size=(10, 10), color=(0, 255, 0)):
    """
    Draws grid lines over an image for visualization.

    Args:
        image (ndarray): Image (numpy array) to draw on.
        grid_size (tuple): (cols, rows) number of grid cells.
        color (tuple): Line color (B, G, R).

    Returns:
        ndarray: Image with grid lines drawn.
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
