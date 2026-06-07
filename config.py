"""Central configuration for the pino LED-tree project.

Import this from new code so the magic numbers (IP, ports, pixel count) live in
one place instead of being copy-pasted across files.
"""

# --- Hardware (Raspberry Pi) ---
NUM_PIXELS = 500
PIXEL_PIN = "D18"          # used as board.D18 on the Pi
PIXEL_ORDER = "GRB"        # wire order of the WS2812 strip
BRIGHTNESS = 0.2

# --- Network (the Pi listens; the laptop connects) ---
PI_HOST = "192.168.1.144"
MAPPING_PORT = 5555        # capturas.py      <-> capturascliente.py
CONTROL_PORT = 4444        # servertest.py    <-> clienttest.py

# --- Mapping data ---
COORDINATES_FILE = "led_coordinates3.json"        # legacy 2D map (studio)
COORDINATES_3D_FILE = "led_coordinates_3d.json"   # 3D map from the wizard

# --- Camera / capture ---
CAMERA_INDEX = 0
CAMERA_FOV_DEG = 60.0      # only used for approximate intrinsics

# --- ArUco floor markers (measure these for your real setup) ---
ARUCO_DICT = "DICT_4X4_50"
MARKER_IDS = (0, 1)
MARKER_LENGTH = 0.15       # printed marker side length (meters)
MARKER_SEPARATION = 0.60   # distance between the two marker centers (meters)

# --- Chessboard calibration ---
CHESSBOARD = (9, 6)        # inner corners (cols, rows)
CHESSBOARD_SQUARE = 0.025  # square size (meters)
CALIBRATION_FILE = "camera_calibration.npz"

# --- Simulator ---
# "synthetic" -> a clean generated cone (all NUM_PIXELS visible, good for testing)
# "captured"  -> use the real positions from COORDINATES_FILE
SIM_LAYOUT = "synthetic"
