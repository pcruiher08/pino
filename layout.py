"""LED positions for the tree, shared by the simulator and the studio UI.

Returns a list of (x, y) per LED. Two modes:
  - "captured":  the real mapped positions from the coordinates JSON
  - "synthetic": a generated cone (all n LEDs)
"""

import json
import math


def synthetic(n):
    """A wound cone — looks like a tree from the front, all n LEDs visible."""
    turns = 14
    pts = []
    for i in range(n):
        t = i / max(n - 1, 1)
        angle = t * turns * 2 * math.pi
        radius = (1.0 - t) * 0.5
        pts.append((radius * math.cos(angle), t))
    return pts


def captured(n, path):
    with open(path) as f:
        data = json.load(f)
    return [(p["x_corrected"], p["y_corrected"]) for p in data][:n]


def captured_3d(n, path):
    """Front projection (x horizontal, z height) of a 3D map from the wizard."""
    with open(path) as f:
        data = json.load(f)
    return [(p["x"], p["z"]) for p in data][:n]


def positions(n, mode, path="led_coordinates3.json"):
    try:
        if mode == "captured":
            pts = captured(n, path)
            if pts:  # show only the LEDs we actually mapped, nothing faked
                return pts
        elif mode == "captured3d":
            pts = captured_3d(n, path)
            if pts:
                return pts
    except (OSError, KeyError, ValueError):
        pass
    return synthetic(n)
