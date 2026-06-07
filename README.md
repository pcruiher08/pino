# pino — camera-mapped smart Christmas tree

A 500-LED WS2812/NeoPixel strip wrapped around a tree, driven by a Raspberry Pi.
A webcam figures out where each LED physically sits, so animations can be aware of
the tree's geometry. (`pino` = "pine" in Spanish.)

## How it works

```
 Laptop (camera + OpenCV)              Raspberry Pi (GPIO D18)
 capturascliente.py  ◄── socket ──►   capturas.py      ──► 500x NeoPixel
 clienttest.py (Tk GUI) ── socket ─►  servertest.py
 plotting*.py / testpoints.py (offline, read the JSON map)
 simulate.py (run animations with no hardware)
```

1. **Map the LEDs.** `capturas.py` (Pi) lights one LED at a time; `capturascliente.py`
   (laptop) watches through the webcam, finds the bright blob, and records its
   `(x, y)`. The result is saved to `led_coordinates*.json`.
2. **Check the map.** `plotting*.py` and `testpoints.py` scatter-plot the saved
   coordinates so you can confirm the capture worked.
3. **Run animations.** `demo.py`, `secuencias.py`, `teststrip.py`, `plotting7.py`
   (rainbow), `servertest.py` + `clienttest.py` (a slider remote), etc.

## 3D LED mapping (capture wizard)

The original mapping was a single camera angle → 2D only. The wizard recovers
real **3D** positions by moving the camera around the tree, using two ArUco
markers on the floor to know where the camera is for each shot.

```bash
python make_markers.py     # generate printable markers + a chessboard (printables/)
python capture_wizard.py   # run the guided wizard
```

Wizard steps (tabs): **Source → Calibration → Markers → Capture → Reconstruct**

1. **Source** — Simulation (no hardware, walks the whole flow) or Hardware
   (webcam + Pi).
2. **Calibration** — load a saved calibration, use approximate intrinsics, or
   capture chessboard shots and calibrate (`camera_calibration.npz`).
3. **Markers** — two floor markers at a known size/separation define the world
   frame (floor = XY, Z up). Set the measured sizes in `config.py`.
4. **Capture** — from each angle, the wizard locks the camera pose from the
   markers and sweeps the LEDs (reusing `capturas.py` on the Pi). Capture ≥ 2
   angles.
5. **Reconstruct** — triangulates every LED seen in ≥ 2 views, shows a rotatable
   3D preview, and saves `led_coordinates_3d.json` (`id, x, y, z, error`).

Try **Simulation** first: pick angles with the slider, capture a few views, and
reconstruct — you'll get a full 3D tree with no camera.

The CV core (`vision.py`) is covered by `python test_vision.py` (synthetic pose
recovery + triangulation). To view a 3D map's front projection in the studio, set
`COORDINATES_FILE = "led_coordinates_3d.json"` and `SIM_LAYOUT = "captured3d"`.

## Setup

Laptop (mapping, plotting, simulator):

```bash
pip install -r requirements.txt
```

Raspberry Pi (physical strip — does not install on a laptop):

```bash
pip install -r requirements-pi.txt
```

Shared settings (IP, ports, pixel count) live in `config.py`.

## Studio — live tree view + animation controls (recommended)

```bash
python studio.py
```

One window: the live tree on the right, controls on the left. Pick an animation,
type a message and hit **Send to tree**, choose a color, switch between the
captured (real) map and a synthetic cone, and adjust speed/brightness — all live.
Rendering is blitted so the controls stay responsive.

Two ways to show text (both use a built-in 5x7 font, `font5x7.py`):

- **Letters** — one big letter at a time, each filling the whole tree. Best on a
  narrow tree, since every letter uses the full LED resolution.
- **Scrolling Text** — a continuous banded scroll; use the **Text size** slider to
  trade letter size for how many characters are visible at once.

The same engine (`animations.py`) drives `scrolltext.py`, so text also runs on the
actual Pi:

```bash
PINO_TEXT="HO HO HO" python scrolltext.py            # on the Pi
PINO_TEXT="HO HO HO" python simulate.py scrolltext.py # laptop
```

## Simulator — test individual animation scripts

`simulate.py` swaps in fake `board` and `neopixel` modules and renders the strip
to a matplotlib window, so any animation script runs **unchanged** on your laptop.

### Launcher

```bash
python launcher.py
```

Pick an animation from the list, choose **Captured (real map)** or **Synthetic
cone**, and hit Play. Switching the layout restarts the current animation.

### Command line

```bash
python simulate.py            # list runnable animations
python simulate.py demo.py    # run one
python simulate.py pi.py
```

Close the window (or press Ctrl-C) to stop.

### LED layout

- **Captured** uses the real mapped positions from `COORDINATES_FILE` (only the
  LEDs actually found by the camera are shown).
- **Synthetic** is a clean generated cone with all `NUM_PIXELS` visible.

Set the default with `SIM_LAYOUT` in `config.py`, override per-run with the
`PINO_SIM_LAYOUT` env var, or just use the launcher's radio buttons.

### Writing a new animation

Write a normal NeoPixel script — see `demo.py` for the template. As long as it uses
`import board` / `import neopixel`, it runs in the simulator and on the Pi with no
changes.
