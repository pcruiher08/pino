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
]

def color_variation_animation():
    duration = 10  
    steps = 100   

    for t in range(steps):
        for i in range(num_pixels):
            color_index = int((i / num_pixels) * len(colors))
            color_start = colors[color_index]
            color_end = colors[(color_index + 1) % len(colors)]

            interpolation_factor = t / steps
            red = int(color_start[0] + (color_end[0] - color_start[0]) * interpolation_factor)
            green = int(color_start[1] + (color_end[1] - color_start[1]) * interpolation_factor)
            blue = int(color_start[2] + (color_end[2] - color_start[2]) * interpolation_factor)

            pixels[i] = (red, green, blue)

        pixels.show()
        

while True:
    color_variation_animation()
