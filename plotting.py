import json
import board
import neopixel
import time


input_filename = "led_coordinates3.json"
with open(input_filename, "r") as json_file:
    led_points = json.load(json_file)



NUM_PIXELS = len(led_points)  
PIXEL_PIN = board.D18  


#y_levels = set(point["y_corrected"] for point in led_points)

#sorted_y_levels = sorted(y_levels)


for point in led_points:
    point["y_corrected"] = point["y_corrected"]
    point["x_corrected"] = point["x_corrected"]


x_coordinates = [point["x_corrected"] for point in led_points]
y_coordinates = [point["y_corrected"] for point in led_points]


led_points.sort(key=lambda point: point["y_corrected"])
equis = [point["id"] for point in led_points]

pixels = neopixel.NeoPixel(PIXEL_PIN, NUM_PIXELS, brightness=0.5, auto_write=False)

#print(led_points)


def turn_on_level(level):
    pixels.fill((0, 0, 0))


    #level_points = [point for point in led_points if point["y_corrected"] == level]

    #for point in level_points:
    #pixel_index = point["id"] % NUM_PIXELS
    pixels[level] = (255, 255, 255)  

    pixels.show()  

for level in equis:
    turn_on_level(level)


print("showing")
