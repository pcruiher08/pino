"""Computer-vision core for 3D LED mapping — hardware-free and unit-testable.

Pipeline:
  1. Calibrate the camera (chessboard) -> intrinsics K + distortion.
  2. Put two ArUco markers on the floor at a known size/separation; this defines
     a world frame (floor = XY plane, Z up).
  3. From each camera viewpoint, recover the camera pose from the markers
     (solvePnP) and record each lit LED's 2D image position.
  4. Triangulate every LED's 3D position from its observations across views.

All functions here are pure (numpy/OpenCV) so they can be tested with synthetic
projections; the camera/Pi I/O lives in capture3d.py.
"""

import cv2
import numpy as np

# ---------------------------------------------------------------- intrinsics

def approx_intrinsics(width, height, fov_deg=60.0):
    """A rough camera matrix from image size and horizontal field of view."""
    f = 0.5 * width / np.tan(np.radians(fov_deg) / 2.0)
    return np.array([[f, 0, width / 2.0],
                     [0, f, height / 2.0],
                     [0, 0, 1.0]], dtype=np.float64)


_CHESS_CRIT = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)


def find_chessboard(gray, pattern):
    """Return refined inner-corner image points for a chessboard, or None."""
    ok, corners = cv2.findChessboardCorners(
        gray, pattern,
        flags=cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE,
    )
    if not ok:
        return None
    return cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), _CHESS_CRIT)


def calibrate_chessboard(corner_sets, image_size, pattern=(9, 6), square_size=0.025):
    """Calibrate from detected chessboard corners.

    corner_sets: list of corner arrays from find_chessboard (one per image).
    image_size:  (width, height). Returns (K, dist, rms, used_count).
    """
    objp = np.zeros((pattern[0] * pattern[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:pattern[0], 0:pattern[1]].T.reshape(-1, 2)
    objp *= square_size
    objpoints = [objp for _ in corner_sets]
    rms, K, dist, _r, _t = cv2.calibrateCamera(
        objpoints, list(corner_sets), image_size, None, None
    )
    return K, dist, rms, len(corner_sets)


# ------------------------------------------------------------------- ArUco

def make_detector(dict_name="DICT_4X4_50"):
    dictionary = cv2.aruco.getPredefinedDictionary(getattr(cv2.aruco, dict_name))
    params = cv2.aruco.DetectorParameters()
    return cv2.aruco.ArucoDetector(dictionary, params), dictionary


def floor_board(marker_len, separation, dictionary, ids=(0, 1)):
    """Two markers lying flat on the floor (Z up).

    Marker `ids[0]` is centered at the world origin; `ids[1]` at (separation, 0, 0).
    `marker_len` and `separation` use the same units (e.g. meters) and set scale.
    """
    h = marker_len / 2.0

    def corners(cx, cy):  # ArUco order: TL, TR, BR, BL, all on the floor (z=0)
        return np.array([[cx - h, cy + h, 0],
                         [cx + h, cy + h, 0],
                         [cx + h, cy - h, 0],
                         [cx - h, cy - h, 0]], dtype=np.float32)

    obj = [corners(0, 0), corners(separation, 0)]
    return cv2.aruco.Board(obj, dictionary, np.array(ids, dtype=np.int32))


def estimate_pose(corners, ids, board, K, dist):
    """Recover camera pose (rvec, tvec) from detected markers, or None."""
    if ids is None or len(ids) == 0:
        return None
    objp, imgp = board.matchImagePoints(corners, ids)
    if objp is None or len(objp) < 4:
        return None
    ok, rvec, tvec = cv2.solvePnP(objp, imgp, K, dist)
    if not ok:
        return None
    return rvec, tvec


def projection_matrix(K, rvec, tvec):
    """World -> image 3x4 projection matrix P = K [R | t]."""
    R, _ = cv2.Rodrigues(rvec)
    return K @ np.hstack([R, tvec.reshape(3, 1)])


# ------------------------------------------------------------- LED detection

def find_led(frame, min_brightness=180):
    """Image position of the single brightest LED, or None if nothing is lit.

    Assumes the lit LED is the brightest thing in view (dark room). Returns a
    sub-pixel (x, y) via the centroid of the bright blob around the peak.
    """
    gray = frame if frame.ndim == 2 else cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    _minv, maxv, _minl, maxloc = cv2.minMaxLoc(gray)
    if maxv < min_brightness:
        return None
    level = max(min_brightness, maxv - 40)
    _ret, mask = cv2.threshold(gray, level, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return (float(maxloc[0]), float(maxloc[1]))
    # blob containing the peak (fall back to the largest)
    peak = max(contours, key=cv2.contourArea)
    for c in contours:
        if cv2.pointPolygonTest(c, (float(maxloc[0]), float(maxloc[1])), False) >= 0:
            peak = c
            break
    m = cv2.moments(peak)
    if m["m00"] == 0:
        return (float(maxloc[0]), float(maxloc[1]))
    return (m["m10"] / m["m00"], m["m01"] / m["m00"])


# ------------------------------------------------------------- triangulation

def triangulate(views):
    """Least-squares 3D point from >=2 observations.

    views: list of (P, (x, y)) where P is a 3x4 projection matrix and (x, y) the
    image point in that view. Returns a length-3 numpy array (world coords).
    """
    rows = []
    for P, (x, y) in views:
        rows.append(x * P[2] - P[0])
        rows.append(y * P[2] - P[1])
    A = np.array(rows, dtype=np.float64)
    _u, _s, vt = np.linalg.svd(A)
    X = vt[-1]
    return X[:3] / X[3]


def reprojection_error(X, views):
    """Mean pixel reprojection error of a 3D point over its views."""
    Xh = np.append(X, 1.0)
    errs = []
    for P, (x, y) in views:
        p = P @ Xh
        errs.append(np.hypot(p[0] / p[2] - x, p[1] / p[2] - y))
    return float(np.mean(errs)) if errs else float("inf")
