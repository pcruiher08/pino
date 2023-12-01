import processing.py

class PointCloudAnimation(processing.py.PApplet):

    def setup(self):
        self.size(600, 600)
        self.background(0)

        self.points = []
        for i in range(1000):
            point = processing.py.PVector(processing.py.random(0, self.width), processing.py.random(0, self.height), processing.py.random(0, 255))
            self.points.append(point)

        self.amplitude = 50
        self.frequency = 2
        self.phase = 0

    def draw(self):
        self.background(0)

        time = self.frameCount / self.frameRate
        for point in self.points:
            z_position = self.amplitude * processing.py.sin(2 * processing.py.PI * self.frequency * time + self.phase)
            point.z = z_position

        for point in self.points:
            self.fill(point.z)
            self.ellipse(point.x, point.y, 5, 5)

