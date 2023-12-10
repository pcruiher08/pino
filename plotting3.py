import time
import board
import neopixel
import numpy as np

num_pixels = 500

pixels = neopixel.NeoPixel(board.D18, num_pixels, auto_write=False)

def update_pixels(frame):
    for i in range(num_pixels):
        frequency = 0.1
        amplitude = 0.5
        phase = frame / 10.0
        color = [
            max(0, min(255, int(255 * amplitude * np.sin(2 * np.pi * frequency * points[i]['x'] + phase)))),
            max(0, min(255, int(255 * amplitude * np.sin(2 * np.pi * frequency * points[i]['y'] + phase)))),
            max(0, min(255, int(255 * amplitude * np.sin(2 * np.pi * frequency * (points[i]['x'] + points[i]['y']) + phase))))
        ]

        pixels[i] = tuple(color)

    pixels.show()
    time.sleep(0.1)

num_frames = 100
for frame in range(num_frames):
    update_pixels(frame)
