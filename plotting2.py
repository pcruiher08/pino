import time
import board
import neopixel
import json
import numpy as np


with open('led_coordinates3.json', 'r') as file:
    led_coordinates = json.load(file)

num_pixels = len(led_coordinates)
pixels = neopixel.NeoPixel(board.D18, num_pixels, auto_write=False)



points = {i: {'x': led_coordinates[i]['x'], 'y': led_coordinates[i]['y'], 'color': [0, 0, 0]} for i in range(num_pixels)}

def update_pixels(frame):
    for i in range(num_pixels):
        frequency = 1.0 / (i + 1)
        amplitude = 0.5
        phase = frame / 10.0
        color = [
            max(0, min(255, int(255 * amplitude * np.sin(2 * np.pi * frequency * points[i]['x'] + phase)))),
            max(0, min(255, int(255 * amplitude * np.sin(2 * np.pi * frequency * points[i]['y'] + phase)))),
            max(0, min(255, int(255 * amplitude * np.sin(2 * np.pi * frequency * (points[i]['x'] + points[i]['y']) + phase))))
        ]
        points[i]['color'] = color

    for i in range(num_pixels):
        pixels[i] = tuple(points[i]['color'])
    pixels.show()
    time.sleep(0.1)

num_frames = 100
for frame in range(num_frames):
    update_pixels(frame)
