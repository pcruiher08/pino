import time
import board
import neopixel

num_pixels = 200
pixel_pin = board.D18

pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.2, auto_write=False, pixel_order=neopixel.RGB)

def turn_on_one_by_one():
    for i in range(num_pixels):
        pixels[i] = (255, 255, 255) 
        pixels.show()
        time.sleep(0.01)  

def turn_off_all():
    pixels.fill((0, 0, 0))
    pixels.show()

try:
    while True:
        turn_on_one_by_one()
        time.sleep(1)  
        turn_off_all()

except KeyboardInterrupt:
    turn_off_all()
