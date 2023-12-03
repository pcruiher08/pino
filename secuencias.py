import time
import board
import neopixel
import random

num_lights = 500
pixel_pin = board.D18 

pixels = neopixel.NeoPixel(pixel_pin, num_lights, brightness=0.2, auto_write=False)

def set_random_color():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

def color_cycle(duration=2, steps=50):
    for _ in range(steps):
        color = set_random_color()
        pixels.fill(color)
        pixels.show()
        time.sleep(duration / steps)

def turn_off_lights():
    pixels.fill((0, 0, 0))
    pixels.show()

try:
    while True:
        color_cycle()
        turn_off_lights()
        time.sleep(2) 

        
except KeyboardInterrupt:
    turn_off_lights()
