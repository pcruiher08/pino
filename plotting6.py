import time
import board
import neopixel
import random

num_pixels = 500

pixels = neopixel.NeoPixel(board.D18, num_pixels, auto_write=False)

def update_pixels():
    for i in range(num_pixels):
        gradient = i / (num_pixels - 1)
        red = int(255 * (1 - gradient))
        green = int(255 * gradient)
        blue = 0
        pixels[num_pixels - i - 1] = (red, green, blue)
        print(red, green, blue)


    pixels.show()
    time.sleep(0.02)

while True:
    update_pixels()
