import board
import neopixel

NUM_PIXELS = 500
PIXEL_PIN = board.D18  

pixels = neopixel.NeoPixel(PIXEL_PIN, NUM_PIXELS, brightness=0.5, auto_write=False)

def turn_on_led(call):
    pixels.fill((0, 0, 0))
    pixels[call] = (255, 255, 255)  
    pixels.show()  

n = int(input())

for i in range(n):
    call = int(input())
    turn_on_led(call)
