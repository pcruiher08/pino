"""Generate printable ArUco floor markers and a calibration chessboard.

    python make_markers.py

Writes PNGs to printables/. Print the two markers, measure the printed side
length and the distance between their centers once placed on the floor, and put
those numbers in config.py (MARKER_LENGTH, MARKER_SEPARATION). Print the
chessboard and measure one square for CHESSBOARD_SQUARE.
"""

import os

import cv2
import numpy as np

import config
import vision


def generate(out_dir="printables", marker_px=600, square_px=100):
    os.makedirs(out_dir, exist_ok=True)
    _detector, dictionary = vision.make_detector(config.ARUCO_DICT)

    for mid in config.MARKER_IDS:
        marker = cv2.aruco.generateImageMarker(dictionary, mid, marker_px)
        quiet = marker_px // 8  # white border so detection is reliable
        canvas = np.full((marker_px + 2 * quiet, marker_px + 2 * quiet), 255, np.uint8)
        canvas[quiet:quiet + marker_px, quiet:quiet + marker_px] = marker
        cv2.imwrite(os.path.join(out_dir, f"marker_{mid}.png"), canvas)

    cols, rows = config.CHESSBOARD          # inner corners
    sq_c, sq_r = cols + 1, rows + 1         # squares
    board = np.zeros((sq_r * square_px, sq_c * square_px), np.uint8)
    for r in range(sq_r):
        for c in range(sq_c):
            if (r + c) % 2 == 0:
                board[r * square_px:(r + 1) * square_px,
                      c * square_px:(c + 1) * square_px] = 255
    cv2.imwrite(os.path.join(out_dir, "chessboard.png"), board)
    return out_dir


if __name__ == "__main__":
    out = generate()
    files = ", ".join(sorted(os.listdir(out)))
    print(f"Wrote to {out}/: {files}")
    print("Print them, then set MARKER_LENGTH / MARKER_SEPARATION / "
          "CHESSBOARD_SQUARE in config.py to your measured sizes.")
