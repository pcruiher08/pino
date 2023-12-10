import time
import board
import neopixel
import random

num_pixels = 500

pixels = neopixel.NeoPixel(board.D18, num_pixels, auto_write=False)

def update_pixels():
    for i in range(num_pixels):
        brightness = random.uniform(0.4, 1.0)  

        red = int(100 * brightness)
        green = int(255 * i / (num_pixels / 2)) if i < num_pixels / 2 else int(255 * (1 - (i - num_pixels / 2) / (num_pixels / 2)))
        blue = 0
        pixels[i] = (red, green, blue)

    pixels.show()
    time.sleep(0.02)

while True:
    update_pixels()
