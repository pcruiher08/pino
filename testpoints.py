import json
import matplotlib.pyplot as plt

input_filename = "led_coordinates.json"
with open(input_filename, "r") as json_file:
    led_points = json.load(json_file)

for point in led_points:
    point["y_corrected"] = point["y_corrected"]
    point["x_corrected"] = point["x_corrected"]


x_coordinates = [point["x_corrected"] for point in led_points]
y_coordinates = [point["y_corrected"] for point in led_points]

plt.scatter(x_coordinates, y_coordinates, marker='o', label='LED Points')

plt.xlabel('X Coordinate')
plt.ylabel('Y Coordinate')
plt.title('LED Points in 2D Plane')

plt.legend()

plt.show()
