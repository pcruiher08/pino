"""Sample animation: a rainbow that scrolls along the strip.

Runs both on the Raspberry Pi and in the simulator:

    python simulate.py demo.py        # laptop
    python demo.py                    # on the Pi
"""

import colorsys
import time

import board
import neopixel

import config

pixels = neopixel.NeoPixel(
    getattr(board, config.PIXEL_PIN),
    config.NUM_PIXELS,
    brightness=config.BRIGHTNESS,
    auto_write=False,
)


def rainbow():
    t = 0.0
    while True:
        for i in range(config.NUM_PIXELS):
            hue = (i / config.NUM_PIXELS + t) % 1.0
            r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
            pixels[i] = (int(r * 255), int(g * 255), int(b * 255))
        pixels.show()
        t += 0.01
        time.sleep(0.02)


if __name__ == "__main__":
    try:
        rainbow()
    except KeyboardInterrupt:
        pixels.fill((0, 0, 0))
        pixels.show()
