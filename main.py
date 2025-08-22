import cv2
from camera import capture_image
from vision import rectification, pothole_cv, mapping
from control import path_planner
from mqtt import mqtt_client
from config import GRID_SIZE, IMAGE_SIZE

#log = #logger.setup_#logger()


def main():
    #mqtt_client.connect()

    # 1. Capture
    frame = capture_image()
    print("Frame captured from camera.")
    # 2. Rectify using ArUco
    # warped = rectification.rectify_frame(frame)
    # print("Frame rectified with ArUco.")
    grid_image = mapping.save_image_with_grid(frame)
    print("Saved at:", grid_image)


    # # 3. Detect pothole

    # Example usage
    result_path = pothole_cv.deduct_pothole(grid_image)
    print("Saved at:", result_path)

    # pothole_px = pothole_cv.detect_potholes(warped)
    # if pothole_px is None:
    #     print("No pothole detected.")
    #     return
    # print(f"Pothole detected at pixels {pothole_px}")

    # 4. Convert to grid
    # take the first detected pothole
   


    #log.info("Path sent to car over MQTT.")


if __name__ == "__main__":
    main()
