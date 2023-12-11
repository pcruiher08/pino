import time
import board
import neopixel
import colorsys
import math

num_pixels = 500

pixels = neopixel.NeoPixel(board.D18, num_pixels, auto_write=False)

colors = [
    (255, 0, 0),   #Red
    (0, 255, 0),   #Green
    (0, 0, 255),   #Blue
]

def color_variation_animation():
    duration = 1 
    steps = 100     

    for t in range(steps):
        for i in range(num_pixels):
            hue = (i / num_pixels + t / steps) % 1.0
            rgb = [int(c * 255) for c in colorsys.hsv_to_rgb(hue, 1.0, 0.5)]
            pixels[i] = (rgb[1], rgb[0], rgb[2])

        pixels.show()
        time.sleep(duration / steps)
    print(rgb)
        

while True:
    color_variation_animation()
