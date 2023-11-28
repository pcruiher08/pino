from manim import *

class RotationsIn3d(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=80 * DEGREES, theta=-60 * DEGREES)

        def func():
            
            param = ParametricFunction(
                lambda u: np.array([
                    2 * u ** 2,
                    4 * u,
                    0
                ]), color=RED, t_range=[0, 1])
            
            
            return param
        curve1 = func()
        curve2 = curve1.copy()
        def update_curve(d,dt):
            d.rotate_about_origin(dt, RIGHT)
        curve2.add_updater(update_curve)
        axes = ThreeDAxes()
        self.add(curve1,curve2)
        self.add(axes)
        self.wait(2*PI)