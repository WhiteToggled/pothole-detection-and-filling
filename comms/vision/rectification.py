import cv2
import numpy as np
from config import DEBUG


def rectify_frame(frame, output_size=(500, 500)):
   
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    params = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(aruco_dict, params)

    corners, ids, _ = detector.detectMarkers(frame)
    if ids is None or len(ids) < 4:
        print("[WARN] Could not detect all 4 ArUco markers.")
        return frame

    # Flatten ids and take marker centers
    ids = ids.flatten()
    centers = [c[0].mean(axis=0) for c in corners]

    # Order points: top-left, top-right, bottom-right, bottom-left
    pts_src = np.array(centers, dtype="float32")
    s = pts_src.sum(axis=1)
    diff = np.diff(pts_src, axis=1)

    ordered = np.zeros((4, 2), dtype="float32")
    ordered[0] = pts_src[np.argmin(s)]      # top-left
    ordered[2] = pts_src[np.argmax(s)]      # bottom-right
    ordered[1] = pts_src[np.argmin(diff)]   # top-right
    ordered[3] = pts_src[np.argmax(diff)]   # bottom-left

    # Destination rectangle
    w, h = output_size
    pts_dst = np.array([[0, 0], [w, 0], [w, h], [0, h]], dtype="float32")

    # Perspective warp
    M = cv2.getPerspectiveTransform(ordered, pts_dst)
    warped = cv2.warpPerspective(frame, M, output_size)

    if DEBUG:
        debug_img = frame.copy()
        for (x, y) in ordered:
            cv2.circle(debug_img, (int(x), int(y)), 5, (0, 0, 255), -1)
        cv2.imshow("Rectification Debug", debug_img)
        cv2.waitKey(1)

    return warped
