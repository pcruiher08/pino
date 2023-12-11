import time
import board
import neopixel
import random
import math as m
num_pixels = 500

pixels = neopixel.NeoPixel(board.D18, num_pixels, auto_write=False)

def update_pixels():
    for t in range(1000):
        for i in range(num_pixels):
            brightness = int(127.5 + 127.5 * m.cos(2 * m.pi * i / num_pixels + t / 50))
            pixels[i] = (0, brightness, 0)
        pixels.show()
        time.sleep(0.02)  

while True:
    update_pixels()
