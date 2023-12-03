import time
import board
import neopixel

num_pixels = 500
pixel_pin = board.D18

pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.2, auto_write=False, pixel_order=neopixel.RGB)

gamma = 2.5

def apply_gamma_correction(value):
    return int(pow(value / 255.0, gamma) * 255 + 0.5)

def turn_on_one_by_one():
    for i in range(num_pixels):
        pixels[i] = (
            apply_gamma_correction(255),
            apply_gamma_correction(255),
            apply_gamma_correction(255),
        )
        pixels.show()
        time.sleep(0.01)  

def turn_off_all():

    pixels.fill((0, 0, 0))
    pixels.show()

def change_intensity():
    for brightness_value in range(1, 10):
        pixels.brightness = brightness_value / 10.0
        pixels.show()
        time.sleep(0.5) 

try:
    while True:
        turn_on_one_by_one()
        time.sleep(1)  
        change_intensity()
        turn_off_all()

except KeyboardInterrupt:
    turn_off_all()
