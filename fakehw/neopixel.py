"""Laptop stand-in for ``neopixel.NeoPixel``.

Implements the parts of the Adafruit NeoPixel API the animations use
(indexing, ``fill``, ``brightness``, ``show``) but renders to a matplotlib
window instead of a physical strip. Drop ``fakehw/`` on the path and existing
animation scripts run unchanged.

Note: ``pixel_order`` only describes hardware wiring on a real strip; the color
you intend is always RGB, so the simulator interprets every tuple as ``(r, g, b)``.
"""

from _simdisplay import get_display

# Pixel-order constants (accepted for API compatibility; see note above).
RGB = "RGB"
GRB = "GRB"
RGBW = "RGBW"
GRBW = "GRBW"


def _rgb(color):
    return (int(color[0]), int(color[1]), int(color[2]))


class NeoPixel:
    def __init__(self, pin, n, *, brightness=1.0, auto_write=True,
                 pixel_order=GRB):
        self.n = n
        self.auto_write = auto_write
        self.pixel_order = pixel_order
        self._brightness = brightness
        self._pixels = [(0, 0, 0)] * n
        self._display = get_display(n)
        self.show()

    def __len__(self):
        return self.n

    def __getitem__(self, index):
        return self._pixels[index]

    def __setitem__(self, index, color):
        if isinstance(index, slice):
            for i, c in zip(range(*index.indices(self.n)), color):
                self._pixels[i] = _rgb(c)
        else:
            self._pixels[index] = _rgb(color)
        if self.auto_write:
            self.show()

    def fill(self, color):
        self._pixels = [_rgb(color)] * self.n
        if self.auto_write:
            self.show()

    @property
    def brightness(self):
        return self._brightness

    @brightness.setter
    def brightness(self, value):
        self._brightness = max(0.0, min(1.0, value))
        self.show()

    def show(self):
        self._display.update(self._pixels, self._brightness)

    def deinit(self):
        self.fill((0, 0, 0))
