import json
import board
import neopixel


input_filename = "led_coordinates.json"
with open(input_filename, "r") as json_file:
    led_points = json.load(json_file)

NUM_PIXELS = len(led_points)  
PIXEL_PIN = board.D18  

ordered_leds = sorted(led_points, key=lambda point: point["x_corrected"])

pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.5, auto_write=False)



for i, point in enumerate(ordered_leds):
    pixel_index = int(i * NUM_PIXELS / len(ordered_leds))  
    red = int((point["x_corrected"] + 50) * 255 / 100)  
    green = int((point["y_corrected"] + 50) * 255 / 100)  
    pixels[pixel_index] = (red, green, 0) 

pixels.show()
