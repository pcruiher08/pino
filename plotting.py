import json
import board
import neopixel
import time


input_filename = "led_coordinates.json"
with open(input_filename, "r") as json_file:
    led_points = json.load(json_file)



NUM_PIXELS = len(led_points)  
PIXEL_PIN = board.D18  

led_points.sort(key=lambda point: point["y_corrected"])

y_levels = set(point["y_corrected"] for point in led_points)

sorted_y_levels = sorted(y_levels)



for point in led_points:
    point["y_corrected"] = -point["y_corrected"]
    point["x_corrected"] = -point["x_corrected"]

pixels = neopixel.NeoPixel(PIXEL_PIN, NUM_PIXELS, brightness=0.5, auto_write=False)


def turn_on_level(level):
    pixels.fill((0, 0, 0))


    level_points = [point for point in led_points if point["y_corrected"] == level]

    for point in level_points:
        pixel_index = point["id"] % NUM_PIXELS
        pixels[pixel_index] = (255, 255, 255)  

    pixels.show()  
    time.sleep(0.5)  

for level in sorted_y_levels:
    turn_on_level(level)


print("showing")
