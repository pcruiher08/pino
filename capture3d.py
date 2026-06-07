"""Capture orchestration for 3D LED mapping.

Two capture sources with the same interface so the wizard works with or without
hardware:

  - HardwareCapturer: real webcam (OpenCV) + the Pi LED sweep over a socket,
    reusing the existing capturas.py protocol (Pi sends each LED index, lights
    it, we grab a frame, find the LED, then ACK).
  - SimCapturer: a synthetic 3D tree projected through a virtual camera, so the
    full reconstruct -> save -> preview flow can be exercised offline.

A CaptureSession collects per-view observations and triangulates them.
"""

import json
import socket

import cv2
import numpy as np

import vision


# ------------------------------------------------------------- calibration io

def save_calibration(path, K, dist, image_size, rms):
    np.savez(path, K=K, dist=dist, image_size=np.array(image_size), rms=rms)


def load_calibration(path):
    data = np.load(path)
    return data["K"], data["dist"], tuple(int(v) for v in data["image_size"])


# ------------------------------------------------------------------ sources

class HardwareCapturer:
    """Real webcam + Pi LED sweep."""

    def __init__(self, K, dist, board, detector, camera_index=0):
        self.K = K
        self.dist = dist
        self.board = board
        self.detector = detector
        self.cap = cv2.VideoCapture(camera_index)

    def grab(self):
        # Flush a couple of buffered frames so we read the current state.
        for _ in range(2):
            self.cap.read()
        ok, frame = self.cap.read()
        if not ok:
            raise RuntimeError("camera read failed")
        return frame

    def detect_pose(self, frame):
        """Return (rvec, tvec) from the floor markers, or None."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = self.detector.detectMarkers(gray)
        return vision.estimate_pose(corners, ids, self.board, self.K, self.dist)

    def projection_for(self, rvec, tvec):
        return vision.projection_matrix(self.K, rvec, tvec)

    def capture_sweep(self, host, port, num_pixels, on_progress=None):
        """One full LED sweep at the current viewpoint -> {led_id: (x, y)}."""
        obs = {}
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(15)
        sock.connect((host, port))
        try:
            while True:
                data = sock.recv(1024).decode()
                if not data:
                    break
                led = int(data)
                pos = vision.find_led(self.grab())
                if pos is not None:
                    obs[led] = pos
                sock.send(b"ACK")
                if on_progress:
                    on_progress(led, num_pixels, pos)
                if led >= num_pixels - 1:
                    break
        finally:
            sock.close()
        return obs

    def release(self):
        if self.cap is not None:
            self.cap.release()


class SimCapturer:
    """Synthetic 3D tree + virtual camera, for hardware-free testing.

    `set_view(azimuth_deg)` moves the virtual camera around the tree; capture and
    pose then reflect that angle. A touch of pixel noise mimics real detection.
    """

    def __init__(self, num_pixels=500, width=1280, height=720, fov_deg=60.0,
                 noise_px=0.4, seed=0):
        self.K = vision.approx_intrinsics(width, height, fov_deg)
        self.dist = np.zeros(5)
        self.size = (width, height)
        self.tree = self._tree(num_pixels)
        self.center = (0.0, 0.0, float(self.tree[:, 2].mean()))
        self.noise_px = noise_px
        self._rng = np.random.RandomState(seed)
        self.set_view(0.0)

    @staticmethod
    def _tree(n):
        pts = []
        for i in range(n):
            t = i / (n - 1)
            ang = t * 14 * 2 * np.pi
            r = (1 - t) * 0.45
            pts.append([r * np.cos(ang), r * np.sin(ang), t * 1.6])
        return np.array(pts, np.float32)

    def set_view(self, azimuth_deg, radius=2.6, height=1.0):
        a = np.radians(azimuth_deg)
        cam = np.array([self.center[0] + radius * np.cos(a),
                        self.center[1] + radius * np.sin(a), height])
        z = np.array(self.center) - cam
        z /= np.linalg.norm(z)
        x = np.cross([0, 0, 1.0], z)
        x /= np.linalg.norm(x)
        y = np.cross(z, x)
        R = np.vstack([x, y, z])
        self._rvec, _ = cv2.Rodrigues(R)
        self._tvec = (-R @ cam).reshape(3, 1)

    def detect_pose(self, frame=None):
        return self._rvec, self._tvec

    def projection_for(self, rvec, tvec):
        return vision.projection_matrix(self.K, rvec, tvec)

    def grab(self):
        return None  # no real frames in sim

    def capture_sweep(self, host, port, num_pixels, on_progress=None):
        """Project the tree from the current view; LEDs facing away are dropped."""
        img, _ = cv2.projectPoints(self.tree, self._rvec, self._tvec,
                                   self.K, self.dist)
        img = img.reshape(-1, 2)
        R, _ = cv2.Rodrigues(self._rvec)
        cam_z = R[2]
        obs = {}
        for led in range(min(num_pixels, len(self.tree))):
            x, y = img[led]
            if not (0 <= x < self.size[0] and 0 <= y < self.size[1]):
                continue
            # Skip LEDs roughly on the far side (very rough self-occlusion).
            depth = cam_z @ self.tree[led] + (-cam_z @ self._cam_pos())
            if depth < 0:
                continue
            nx = x + self._rng.randn() * self.noise_px
            ny = y + self._rng.randn() * self.noise_px
            obs[led] = (float(nx), float(ny))
            if on_progress:
                on_progress(led, num_pixels, (nx, ny))
        return obs

    def _cam_pos(self):
        R, _ = cv2.Rodrigues(self._rvec)
        return (-R.T @ self._tvec).ravel()

    def release(self):
        pass


# ------------------------------------------------------------------ session

class CaptureSession:
    """Collects per-view observations and triangulates the LEDs."""

    def __init__(self):
        self.views = []  # list of (P, {led: (x, y)})

    def add_view(self, P, obs):
        self.views.append((P, dict(obs)))

    @property
    def num_views(self):
        return len(self.views)

    def _per_led(self):
        per = {}
        for P, obs in self.views:
            for led, xy in obs.items():
                per.setdefault(led, []).append((P, xy))
        return per

    def reconstruct(self, min_views=2, max_error=8.0):
        """Triangulate every LED seen in >= min_views. Returns {led: (xyz, err)}."""
        out = {}
        for led, vs in self._per_led().items():
            if len(vs) < min_views:
                continue
            X = vision.triangulate(vs)
            err = vision.reprojection_error(X, vs)
            if err <= max_error:
                out[led] = (X, err)
        return out

    def save(self, path, points):
        """Write [{id, x, y, z, error}] with x,y centered and z = height."""
        if not points:
            raise ValueError("nothing reconstructed")
        xy = np.array([[p[0][0], p[0][1]] for p in points.values()])
        cx, cy = xy.mean(axis=0)
        rows = []
        for led in sorted(points):
            X, err = points[led]
            rows.append({
                "id": int(led),
                "x": float(X[0] - cx),
                "y": float(X[1] - cy),
                "z": float(X[2]),
                "error": float(err),
            })
        with open(path, "w") as f:
            json.dump(rows, f, indent=2)
        return rows
