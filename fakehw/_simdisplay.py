"""matplotlib-backed renderer for the NeoPixel simulator.

Holds a single window. ``NeoPixel.show()`` calls :meth:`_Display.update`, which
repaints every LED at its layout position with its current color and brightness.
Closing the window raises ``KeyboardInterrupt`` so animation scripts run their
usual cleanup (``except KeyboardInterrupt: turn_off``) and exit.
"""

import os

import matplotlib.pyplot as plt

import layout

try:
    import config
except ImportError:  # running without the project root on the path
    config = None


def _cfg(name, default):
    return getattr(config, name, default) if config else default


def _layout(n):
    # PINO_SIM_LAYOUT env var wins over config so the launcher can override it.
    mode = os.environ.get("PINO_SIM_LAYOUT") or _cfg("SIM_LAYOUT", "synthetic")
    path = _cfg("COORDINATES_FILE", "led_coordinates3.json")
    return layout.positions(n, mode, path)


class _Display:
    def __init__(self, n):
        self.n = n
        self.coords = _layout(n)
        self.points = len(self.coords)  # may be < n when using the captured map
        self.closed = False

        plt.ion()
        self.fig, self.ax = plt.subplots(figsize=(5, 8))
        self.fig.canvas.manager.set_window_title("pino simulator")
        self.fig.patch.set_facecolor("black")
        self.ax.set_facecolor("black")

        xs = [c[0] for c in self.coords]
        ys = [c[1] for c in self.coords]
        self.scatter = self.ax.scatter(
            xs, ys, s=50, c=[(0.0, 0.0, 0.0)] * self.points, edgecolors="none"
        )
        self.ax.set_aspect("equal")
        self.ax.axis("off")
        self.ax.set_title("close window to stop", color="0.6", fontsize=9)
        self.fig.canvas.mpl_connect("close_event", self._on_close)
        plt.show(block=False)

    def _on_close(self, _event):
        self.closed = True

    def update(self, pixels, brightness):
        if self.closed:
            raise KeyboardInterrupt("Simulator window closed")
        colors = [
            (
                min(c[0], 255) / 255 * brightness,
                min(c[1], 255) / 255 * brightness,
                min(c[2], 255) / 255 * brightness,
            )
            for c in pixels[:self.points]
        ]
        self.scatter.set_color(colors)
        self.fig.canvas.draw_idle()
        plt.pause(0.001)


_display = None


def get_display(n):
    global _display
    if _display is None or _display.n != n:
        _display = _Display(n)
    return _display
