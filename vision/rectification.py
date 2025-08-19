import cv2
import numpy as np


def rectify_frame(frame, marker_length=0.05):
    """
    Warp the input frame using 4 ArUco markers placed at corners of the map.
    Args:
        frame (np.ndarray): input BGR image
        marker_length (float): marker size in meters (not critical for demo)

    Returns:
        np.ndarray: warped, top-down aligned map image
    """
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    params = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(aruco_dict, params)

    corners, ids, _ = detector.detectMarkers(frame)
    if ids is None or len(ids) < 4:
        print("[WARN] Could not detect all 4 ArUco markers.")
        return frame

    # Sort markers by ID for consistency
    ids = ids.flatten()
    sorted_idx = np.argsort(ids)
    corners = [corners[i][0] for i in sorted_idx]

    # Expected corners: top-left, top-right, bottom-right, bottom-left
    pts_src = np.array([c.mean(axis=0) for c in corners], dtype="float32")
    pts_dst = np.array(
        [[0, 0], [500, 0], [500, 500], [0, 500]], dtype="float32")

    M = cv2.getPerspectiveTransform(pts_src, pts_dst)
    warped = cv2.warpPerspective(frame, M, (500, 500))
    return warped
