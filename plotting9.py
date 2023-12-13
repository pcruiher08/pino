import time
import board
import neopixel
import random

num_pixels = 500

pixels = neopixel.NeoPixel(board.D18, num_pixels, auto_write=False)

def animation():
    background_color = (150, 150, 100)
    pixels.fill(background_color)
    pixels.show()

    num_flashes = 20

    for _ in range(num_flashes):
        flash_pixel = random.randint(0, num_pixels - 1)

        flash_color = (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
        )

        pixels[flash_pixel] = flash_color
        pixels.show()
        time.sleep(0.5)

        pixels[flash_pixel] = background_color
        pixels.show()
        time.sleep(0.5)


while True:
    animation()
