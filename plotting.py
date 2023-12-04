import json
import board
import neopixel


input_filename = "led_coordinates.json"
with open(input_filename, "r") as json_file:
    led_points = json.load(json_file)



NUM_PIXELS = len(led_points)  
PIXEL_PIN = board.D18  

ordered_leds = sorted(led_points, key=lambda point: point["x_corrected"])

for point in ordered_leds:
    point["y_corrected"] = -point["y_corrected"]
    point["x_corrected"] = -point["x_corrected"]

pixels = neopixel.NeoPixel(PIXEL_PIN, NUM_PIXELS, brightness=0.5, auto_write=False)



for point in led_points:
    if abs(point["x_corrected"] - point["y_corrected"]) < 10:  
        color = (255, 255, 255)  
        pixels[point["id"]] = color  
        pixels.show()



print("showing")
