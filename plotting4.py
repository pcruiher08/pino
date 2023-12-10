import time
import board
import neopixel
import numpy as np
import colorsys
import random

num_pixels = 500

pixels = neopixel.NeoPixel(board.D18, num_pixels, auto_write=False)

def map_value(value, in_min, in_max, out_min, out_max):
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def update_pixels(frame):
    for i in range(num_pixels):
        brightness = min(1.0, max(0.0, np.sin((i + frame) / 10.0) + random.uniform(0, 0.5)))

        hue = map_value(brightness, 0, 1, 0.0, 0.1)
        rgb_color = colorsys.hsv_to_rgb(hue, 1.0, brightness)
        color = [int(255 * channel) for channel in rgb_color[::-1]]
        pixels[i] = tuple(color)

    pixels.show()

while True:
    for frame in range(100): 
        update_pixels(frame)
