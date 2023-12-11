import json
import matplotlib.pyplot as plt

input_filename = "led_coordinates3.json"
with open(input_filename, "r") as json_file:
    led_points = json.load(json_file)

for point in led_points:
    point["y_corrected"] = point["y_corrected"]
    point["x_corrected"] = point["x_corrected"]


x_coordinates = [point["x_corrected"] for point in led_points]
y_coordinates = [point["y_corrected"] for point in led_points]

x_coordinates_original = [point["x"] for point in led_points]
y_coordinates_original = [point["y"] for point in led_points]


plt.subplot(1, 2, 1)
plt.ylabel('Y Coordinate')
plt.title('LED Points in 2D Plane no correction')


plt.scatter(x_coordinates_original, y_coordinates_original, marker='o')

plt.subplot(1, 2, 2)
plt.scatter(x_coordinates, y_coordinates, marker='o', label='LED Points')

for i in range(len(led_points)):
    plt.annotate(led_points[i]["id"], (led_points[i]["x_corrected"], led_points[i]["y_corrected"]))

plt.xlabel('X Coordinate')
plt.title('LED Points in 2D Plane')

plt.legend()

plt.show()
