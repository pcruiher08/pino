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

def color_variation_animation(color, wait):
    duration = 1 
    steps = 100     


    for i in range(num_pixels):
        pixels[i] = color
        pixels.show()
        time.sleep(wait)


        #pixels[i] = (rgb[1], rgb[0], rgb[2])

        pixels.show()
        time.sleep(duration / steps)
   
        

while True:
    color_variation_animation((0,120,120), 0)
