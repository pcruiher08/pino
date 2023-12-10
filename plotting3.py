import time
import board
import neopixel
import numpy as np
import colorsys

num_pixels = 500

pixels = neopixel.NeoPixel(board.D18, num_pixels, auto_write=False)

def update_pixels(frame):
    for i in range(num_pixels):
        frequency = 0.5
        amplitude = 0.7
        phase = frame / 5.0
        hue = (np.sin(2 * np.pi * frequency * i + phase) + 1) / 2.0
        rgb_color = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
        color = [int(255 * amplitude * channel) for channel in rgb_color]
        pixels[i] = tuple(color)

    pixels.show()

num_frames = 5000
for frame in range(num_frames):
    update_pixels(frame)
