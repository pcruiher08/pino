import time
import board
import neopixel
import random
import math
num_pixels = 500

pixels = neopixel.NeoPixel(board.D18, num_pixels, auto_write=False)

def update_pixels():
    for t in range(1000):  
        for i in range(num_pixels):
            red = int(127.5 + 127.5 * math.cos(2 * math.pi * i / num_pixels + t / 50))
            green = int(127.5 + 127.5 * math.cos(2 * math.pi * i / num_pixels + t / 30))
            blue = int(127.5 + 127.5 * math.cos(2 * math.pi * i / num_pixels + t / 20))
            pixels[i] = (red, green, blue)
    pixels.show()

while True:
    update_pixels()
