import time
import board
import neopixel
import math

num_pixels = 500

pixels = neopixel.NeoPixel(board.D18, num_pixels, auto_write=False)

colors = [
    (255, 0, 0),   #Red
    (0, 255, 0),   #Green
    (0, 0, 255),   #Blue
    (255, 255, 0), #Yellow
    (255, 0, 255), #Magenta
    (0, 255, 255), #Cyan
]

def color_variation_animation():
    for t in range(1000):
        for i in range(num_pixels):
            color_index = int((i / num_pixels) * len(colors))
            pixels[i] = colors[color_index]
        pixels.show()
    

while True:
    color_variation_animation()
