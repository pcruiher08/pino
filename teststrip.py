import time
import board
import neopixel

num_pixels = 50
pixel_pin = board.D18  
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.2, auto_write=False, pixel_order=neopixel.RGB)

def turn_on_leds():
    pixels.fill((255, 0, 0)) 
    pixels.show()

def turn_off_leds():
    pixels.fill((0, 0, 0))  
    pixels.show()

try:
    while True:
        turn_on_leds()
        time.sleep(2)  
        turn_off_leds()
        time.sleep(2)  

except KeyboardInterrupt:
    turn_off_leds()
