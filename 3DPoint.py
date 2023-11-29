from manim import *
import random
import math as m
import json
import os

class RotationsIn3dSphere(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=60 * DEGREES, theta=25 * DEGREES, focal_distance=30, zoom=1.2)
    
        #sphere1 = Sphere(center=(1, 1, 1), radius=0.01, color=BLUE)
        #sphere2 = Sphere(center=(1, 1, 2), radius=0.01, color=RED)
        #spheres = [sphere1, sphere2]

        def update_sphere(d, dt):
            d.rotate_about_origin(dt, IN)

        axes = ThreeDAxes()

        cone_radius = 1.2
        cone_height = 2.3
        cone_shift =  2.3

        cone = Cone(base_radius=cone_radius, height=cone_height, direction=OUT, show_base=True, v_range=(0, 2 * PI), u_min=0)
        cone.set_opacity(0.4)
        cone.set_color((128,0,128))
        cone.shift(cone_shift * OUT)  
        self.add(cone, axes)
        spheres = []
        points = []
        sphere_radius = 0.01
        max_z_percentage = 0.8 

        if os.path.exists("points.json"):
            print("reading")
 
            with open("points.json", "r") as f:
                points = json.load(f)
        else:
            print("rewriting")
            for _ in range(500):
                max_shifted_z = cone_height * max_z_percentage
                shifted_z = random.uniform(max_shifted_z * 0.09, max_shifted_z) 

                if shifted_z < cone_height:
                    max_x = cone_radius * m.sqrt(1 - (shifted_z / cone_height) ** 2)
                    max_y = cone_radius * m.sqrt(1 - (shifted_z / cone_height) ** 2)
                else:
                    max_x = 0
                    max_y = 0

                x = random.uniform(-max_x + max_x * 0.3, max_x - max_x * 0.3)
                y = random.uniform(-max_y + max_x * 0.3, max_y - max_x * 0.3)

                z = shifted_z * (1 - (x**2 + y**2) / cone_radius**2)

                
                #sphere = Sphere(radius=sphere_radius)
                #sphere.shift((x ) * RIGHT + (y ) * UP + (z ) * OUT)

                points.append([x , y , z ])
                
         
            with open("points.json", "w") as f:
                json.dump(points, f, indent=4)

        #print(len(spheres))
        #print(points)
        print("building")

        for point in points:
            sphere = Sphere(radius=sphere_radius)
            sphere.shift((point[0] ) * RIGHT + (point[1] ) * UP + (point[2] ) * OUT)
            sphere.add_updater(update_sphere)
            self.add(sphere, axes)


        print("animation")
        fast = 0.01

        self.wait(2 * PI * fast)


##manim --disable_caching -pql 3DPoint.py RotationsIn3dSphere