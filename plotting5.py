import time
import board
import neopixel
import random

num_pixels = 500
pixels = neopixel.NeoPixel(board.D18, num_pixels, auto_write=False)

def update_pixels():
    for i in range(num_pixels):
        brightness = random.uniform(0.4, 1.0) 
        color = [
            int(0 * brightness),  
            int(0 * brightness),  
            int(255 * brightness)     
        ]
        pixels[i] = tuple(color)

    pixels.show()
  

while True:
    update_pixels()
