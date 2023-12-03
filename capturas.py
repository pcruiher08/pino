import time
import board
import neopixel

num_pixels = 500
pixel_pin = board.D18 

pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.5, auto_write=False)

def turn_on_led(led_number):
    pixels.fill((0, 0, 0))  
    pixels[led_number] = (255, 255, 255)  
    pixels.show()
    print("LED:", led_number)

try:
    for led in range(num_pixels):
        turn_on_led(led)
        time.sleep(0.5)  

except KeyboardInterrupt:
    pixels.fill((0, 0, 0))  
    pixels.show()
