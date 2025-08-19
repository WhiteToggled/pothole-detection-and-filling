import cv2
from camera import get_frame
from vision import aruco_utils, pothole_cv, mapping
from utils import logger, draw
from control import path_planner
from mqtt import mqtt_client
from config import GRID_SIZE, IMAGE_SIZE

log = logger.setup_logger()


def main():
    mqtt_client.connect()

    # 1. Capture
    frame = get_frame()
    log.info("Frame captured from camera.")

    # 2. Rectify using ArUco
    warped = aruco_utils.rectify_frame(frame)
    log.info("Frame rectified with ArUco.")

    # 3. Detect pothole
    pothole_px = pothole_cv.detect_pothole(warped)
    if pothole_px is None:
        log.warning("No pothole detected.")
        return
    log.info(f"Pothole detected at pixels {pothole_px}")

    # 4. Convert to grid
    pothole_cell = mapping.pixel_to_grid(pothole_px, IMAGE_SIZE, GRID_SIZE)
    log.info(f"Pothole mapped to grid {pothole_cell}")

    # Demo: assume car starts at bottom-center
    start = (GRID_SIZE[1]-1, GRID_SIZE[0]//2)

    # 5. Plan path
    grid = [[0]*GRID_SIZE[0] for _ in range(GRID_SIZE[1])]
    path = path_planner.plan_path(
        grid, start, (pothole_cell[1], pothole_cell[0]))
    log.info(f"Path planned with {len(path)} steps.")

    # 6. Draw + show
    overlay = mapping.draw_grid(warped, GRID_SIZE)
    overlay = pothole_cv.draw_pothole(overlay, pothole_px)
    overlay = draw.draw_path(overlay, path, GRID_SIZE)
    cv2.imshow("Result", overlay)
    cv2.waitKey(0)

    # 7. Send via MQTT
    mqtt_client.publish_message({"path": path})
    log.info("Path sent to car over MQTT.")


if __name__ == "__main__":
    main()
