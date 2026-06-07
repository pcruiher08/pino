"""Scrolling text on the tree — runs on the Raspberry Pi and in the simulator.

    python scrolltext.py                         # on the Pi
    python simulate.py scrolltext.py             # laptop
    PINO_TEXT="HO HO HO" python simulate.py scrolltext.py

Set the text with the PINO_TEXT environment variable (default "MERRY CHRISTMAS").
The studio UI (studio.py) is the interactive way to drive this.
"""

import os
import time

import board
import neopixel

import animations
import config
import layout

coords = layout.positions(config.NUM_PIXELS, config.SIM_LAYOUT,
                          config.COORDINATES_FILE)
norm = animations.normalize(coords)

pixels = neopixel.NeoPixel(
    getattr(board, config.PIXEL_PIN),
    config.NUM_PIXELS,
    brightness=config.BRIGHTNESS,
    auto_write=False,
)

anim = animations.ScrollingText(
    norm, text=os.environ.get("PINO_TEXT", "MERRY CHRISTMAS")
)

frame = 0
try:
    while True:
        for i, color in enumerate(anim.render(frame)):
            pixels[i] = color
        pixels.show()
        frame += 1
        time.sleep(0.03)
except KeyboardInterrupt:
    pixels.fill((0, 0, 0))
    pixels.show()
