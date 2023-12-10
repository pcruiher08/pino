import time
import board
import neopixel
import numpy as np
import colorsys
import random

num_pixels = 500

pixels = neopixel.NeoPixel(board.D18, num_pixels, auto_write=False)

def update_pixels(frame):
    for i in range(num_pixels):
        brightness = min(1.0, max(0.0, np.sin((i + frame) / 10.0) + random.uniform(0, 0.5)))

        color = [
            int(255 * brightness),
            int(255 * brightness * 0.5),
            0
        ]
        pixels[i] = tuple(color)

    pixels.show()

while True:
    for frame in range(100):  
        update_pixels(frame)
