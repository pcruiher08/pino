import time
import board
import neopixel

num_pixels = 50
pixel_pin = board.D18

pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brißghtness=0.2, auto_write=False, pixel_order=neopixel.RGB)

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

        for brightness_value in range(1, 10):
            pixels.brightness = brightness_value / 10.0
            pixels.show()
            time.sleep(0.5)

        turn_off_all()

        for brightness_value in range(9, 0, -1):
            pixels.brightness = brightness_value / 10.0
            pixels.show()
            time.sleep(0.5)

        pixels.show()
        time.sleep(0.1)

def turn_off_all():
    pixels.fill((0, 0, 0))
    pixels.show()



except KeyboardInterrupt:
    turn_off_all()
