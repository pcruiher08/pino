import json
import matplotlib.pyplot as plt

with open("points.json", "r") as f:
    points = json.load(f)

x = [point[0] for point in points]
y = [point[1] for point in points]
z = [point[2] for point in points]

plt.figure(figsize=(10, 6))
plt.scatter(x, y, c=z, cmap="viridis", alpha=0.7)
plt.xlabel("X")
plt.ylabel("Y")
plt.title("Points Inside the Cone")
plt.colorbar()
plt.show()