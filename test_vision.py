"""Synthetic tests for vision.py — no camera or Pi needed.

Builds a known 3D tree, places virtual cameras around it, projects the LEDs into
each view, and checks that pose recovery and triangulation reproduce the truth.

    python test_vision.py
"""

import cv2
import numpy as np

import vision

W, H = 1280, 720
K = vision.approx_intrinsics(W, H, 60.0)
DIST = np.zeros(5)


def look_at(cam_pos, target, up=(0, 0, 1)):
    """World->camera rvec, tvec for a camera at cam_pos looking at target."""
    cam_pos = np.array(cam_pos, float)
    z = np.array(target, float) - cam_pos
    z /= np.linalg.norm(z)
    x = np.cross(np.array(up, float), z)
    x /= np.linalg.norm(x)
    y = np.cross(z, x)
    R = np.vstack([x, y, z])           # rows = camera axes in world
    t = -R @ cam_pos
    rvec, _ = cv2.Rodrigues(R)
    return rvec, t.reshape(3, 1)


def synthetic_tree(n=60):
    pts = []
    for i in range(n):
        t = i / (n - 1)
        ang = t * 12 * 2 * np.pi
        r = (1 - t) * 0.4
        pts.append([r * np.cos(ang), r * np.sin(ang), t * 1.5])
    return np.array(pts, np.float32)


def camera_ring(center, radius, height, count):
    poses = []
    for k in range(count):
        a = 2 * np.pi * k / count
        c = [center[0] + radius * np.cos(a), center[1] + radius * np.sin(a), height]
        poses.append(look_at(c, center))
    return poses


def test_triangulation():
    tree = synthetic_tree(60)
    center = (0, 0, 0.75)
    poses = camera_ring(center, radius=2.5, height=0.9, count=4)

    Ps, projected = [], []
    for rvec, tvec in poses:
        Ps.append(vision.projection_matrix(K, rvec, tvec))
        img, _ = cv2.projectPoints(tree, rvec, tvec, K, DIST)
        projected.append(img.reshape(-1, 2))

    errs = []
    for i, truth in enumerate(tree):
        views = [(Ps[v], tuple(projected[v][i])) for v in range(len(Ps))]
        X = vision.triangulate(views)
        errs.append(np.linalg.norm(X - truth))
    err = float(np.max(errs))
    assert err < 1e-3, f"triangulation error too high: {err}"
    print(f"triangulation: max 3D error = {err:.2e} m over {len(tree)} LEDs  OK")


def test_pose_from_markers():
    detector, dictionary = vision.make_detector("DICT_4X4_50")
    board = vision.floor_board(marker_len=0.15, separation=0.6, dictionary=dictionary)

    rvec, tvec = look_at((1.5, -1.5, 1.0), (0.3, 0, 0))
    # Project the two markers' corners to make a synthetic detection.
    obj = np.array([board.getObjPoints()[m][c]
                    for m in range(2) for c in range(4)], np.float32)
    img, _ = cv2.projectPoints(obj, rvec, tvec, K, DIST)
    img = img.reshape(2, 4, 2).astype(np.float32)
    corners = [img[0].reshape(1, 4, 2), img[1].reshape(1, 4, 2)]
    ids = np.array([[0], [1]])

    pose = vision.estimate_pose(corners, ids, board, K, DIST)
    assert pose is not None, "pose estimation failed"
    r2, t2 = pose
    r_err = float(np.linalg.norm(r2 - rvec))
    t_err = float(np.linalg.norm(t2 - tvec))
    assert r_err < 1e-3 and t_err < 1e-3, f"pose error r={r_err} t={t_err}"
    print(f"pose: rvec err={r_err:.2e}, tvec err={t_err:.2e} m  OK")


def test_find_led():
    frame = np.zeros((H, W), np.uint8)
    cv2.circle(frame, (900, 300), 6, 255, -1)
    pos = vision.find_led(frame)
    assert pos is not None
    err = np.hypot(pos[0] - 900, pos[1] - 300)
    assert err < 2.0, f"led centroid off by {err}"
    assert vision.find_led(np.zeros((H, W), np.uint8)) is None
    print(f"find_led: centroid err={err:.2f}px, blank->None  OK")


if __name__ == "__main__":
    test_find_led()
    test_pose_from_markers()
    test_triangulation()
    print("\nall vision tests passed")
