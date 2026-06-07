#!/usr/bin/env python3
"""Guided wizard to map the tree's LEDs in 3D.

    python capture_wizard.py

Steps (tabs): Source -> Calibration -> Markers -> Capture -> Reconstruct.
Choose "Simulation" to walk the whole flow with no hardware, or "Hardware" to
calibrate a real webcam, recover camera pose from two floor ArUco markers, sweep
the LEDs from several angles, and triangulate their 3D positions.
"""

import tkinter as tk
from tkinter import messagebox, ttk

import numpy as np

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import capture3d
import config
import vision


class Wizard:
    def __init__(self, root):
        self.root = root
        root.title("pino — 3D capture wizard")

        # pipeline state
        self.K = None
        self.dist = None
        self.board = None
        self.detector = None
        self.capturer = None
        self.session = capture3d.CaptureSession()
        self.points = None
        self.chess_corners = []
        self.image_size = (1280, 720)

        self.nb = ttk.Notebook(root)
        self.nb.pack(fill="both", expand=True, padx=8, pady=8)
        self._build_source()
        self._build_calibration()
        self._build_markers()
        self._build_capture()
        self._build_reconstruct()

        self.status = ttk.Label(root, text="Start on the Source tab.",
                                relief="sunken", anchor="w")
        self.status.pack(fill="x", side="bottom")

    def say(self, msg):
        self.status.config(text=msg)

    # ----------------------------------------------------------- Source
    def _build_source(self):
        f = ttk.Frame(self.nb, padding=12)
        self.nb.add(f, text="1. Source")

        self.source = tk.StringVar(value="sim")
        ttk.Radiobutton(f, text="Simulation (no hardware)", value="sim",
                        variable=self.source).pack(anchor="w")
        ttk.Radiobutton(f, text="Hardware (webcam + Pi)", value="hardware",
                        variable=self.source).pack(anchor="w")

        grid = ttk.Frame(f)
        grid.pack(anchor="w", pady=8)
        self.num_pixels = tk.IntVar(value=config.NUM_PIXELS)
        self.camera_index = tk.IntVar(value=config.CAMERA_INDEX)
        self.pi_host = tk.StringVar(value=config.PI_HOST)
        self.pi_port = tk.IntVar(value=config.MAPPING_PORT)
        for r, (lbl, var) in enumerate([
            ("LED count", self.num_pixels), ("Camera index", self.camera_index),
            ("Pi host", self.pi_host), ("Pi port", self.pi_port)]):
            ttk.Label(grid, text=lbl).grid(row=r, column=0, sticky="w", padx=4, pady=2)
            ttk.Entry(grid, textvariable=var, width=18).grid(row=r, column=1, pady=2)

        ttk.Button(f, text="Start", command=self.start_source).pack(anchor="w")

    def start_source(self):
        if self.source.get() == "sim":
            self.capturer = capture3d.SimCapturer(num_pixels=self.num_pixels.get())
            self.K, self.dist = self.capturer.K, self.capturer.dist
            self.image_size = self.capturer.size
            self.say("Simulation ready. Calibration is optional (approx intrinsics set).")
        else:
            self.capturer = None  # built at capture time once K + board exist
            self.say("Hardware selected. Do Calibration, then Markers, then Capture.")
        messagebox.showinfo("Source", f"Source set to {self.source.get()}.")

    # -------------------------------------------------------- Calibration
    def _build_calibration(self):
        f = ttk.Frame(self.nb, padding=12)
        self.nb.add(f, text="2. Calibration")

        ttk.Button(f, text=f"Load {config.CALIBRATION_FILE}",
                   command=self.load_calib).pack(anchor="w", pady=2)
        ttk.Button(f, text="Use approximate intrinsics (from FOV)",
                   command=self.approx_calib).pack(anchor="w", pady=2)
        ttk.Separator(f, orient="horizontal").pack(fill="x", pady=6)
        ttk.Label(f, text="Chessboard calibration (hardware):").pack(anchor="w")
        ttk.Button(f, text="Grab chessboard shot",
                   command=self.grab_chessboard).pack(anchor="w", pady=2)
        ttk.Button(f, text="Calibrate from shots",
                   command=self.run_calibration).pack(anchor="w", pady=2)
        ttk.Button(f, text=f"Save to {config.CALIBRATION_FILE}",
                   command=self.save_calib).pack(anchor="w", pady=2)
        self.calib_status = ttk.Label(f, text="No calibration yet.")
        self.calib_status.pack(anchor="w", pady=(8, 0))

    def load_calib(self):
        try:
            self.K, self.dist, self.image_size = \
                capture3d.load_calibration(config.CALIBRATION_FILE)
            self.calib_status.config(text=f"Loaded calibration {self.image_size}.")
            self.say("Calibration loaded.")
        except Exception as e:  # noqa: BLE001
            messagebox.showerror("Load failed", str(e))

    def approx_calib(self):
        w, h = self.image_size
        self.K = vision.approx_intrinsics(w, h, config.CAMERA_FOV_DEG)
        self.dist = np.zeros(5)
        self.calib_status.config(text=f"Approximate intrinsics set for {w}x{h}.")
        self.say("Using approximate intrinsics.")

    def grab_chessboard(self):
        cap = self._hw_capturer_for_preview()
        if cap is None:
            return
        try:
            frame = cap.grab()
        except Exception as e:  # noqa: BLE001
            messagebox.showerror("Camera", str(e))
            return
        import cv2
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        self.image_size = (gray.shape[1], gray.shape[0])
        corners = vision.find_chessboard(gray, config.CHESSBOARD)
        if corners is None:
            self.say("No chessboard found in that shot — reposition and retry.")
            return
        self.chess_corners.append(corners)
        self.calib_status.config(text=f"{len(self.chess_corners)} chessboard shots.")
        self.say(f"Captured shot {len(self.chess_corners)} (need ~10-15).")

    def run_calibration(self):
        if len(self.chess_corners) < 5:
            messagebox.showwarning("Calibration", "Capture at least 5 shots first.")
            return
        self.K, self.dist, rms, used = vision.calibrate_chessboard(
            self.chess_corners, self.image_size, config.CHESSBOARD,
            config.CHESSBOARD_SQUARE)
        self.calib_status.config(text=f"Calibrated: rms={rms:.3f}px over {used} shots.")
        self.say("Calibration complete.")

    def save_calib(self):
        if self.K is None:
            messagebox.showwarning("Calibration", "Nothing to save yet.")
            return
        rms = 0.0
        capture3d.save_calibration(config.CALIBRATION_FILE, self.K, self.dist,
                                   self.image_size, rms)
        self.say(f"Saved {config.CALIBRATION_FILE}.")

    # ------------------------------------------------------------ Markers
    def _build_markers(self):
        f = ttk.Frame(self.nb, padding=12)
        self.nb.add(f, text="3. Markers")

        grid = ttk.Frame(f)
        grid.pack(anchor="w")
        self.dict_name = tk.StringVar(value=config.ARUCO_DICT)
        self.marker_len = tk.DoubleVar(value=config.MARKER_LENGTH)
        self.separation = tk.DoubleVar(value=config.MARKER_SEPARATION)
        for r, (lbl, var) in enumerate([
            ("ArUco dictionary", self.dict_name),
            ("Marker length (m)", self.marker_len),
            ("Marker separation (m)", self.separation)]):
            ttk.Label(grid, text=lbl).grid(row=r, column=0, sticky="w", padx=4, pady=2)
            ttk.Entry(grid, textvariable=var, width=18).grid(row=r, column=1, pady=2)

        ttk.Button(f, text="Build board", command=self.build_board).pack(anchor="w", pady=4)
        ttk.Button(f, text="Test pose (hardware)",
                   command=self.test_pose).pack(anchor="w", pady=2)
        self.marker_status = ttk.Label(f, text="No board yet.")
        self.marker_status.pack(anchor="w", pady=(8, 0))

    def build_board(self):
        try:
            self.detector, dictionary = vision.make_detector(self.dict_name.get())
            self.board = vision.floor_board(self.marker_len.get(),
                                            self.separation.get(), dictionary,
                                            config.MARKER_IDS)
            self.marker_status.config(text="Board built.")
            self.say("ArUco board ready.")
        except Exception as e:  # noqa: BLE001
            messagebox.showerror("Board", str(e))

    def test_pose(self):
        cap = self._hw_capturer_for_preview()
        if cap is None or self.board is None:
            messagebox.showwarning("Pose", "Build the board and start hardware first.")
            return
        try:
            frame = cap.grab()
        except Exception as e:  # noqa: BLE001
            messagebox.showerror("Camera", str(e))
            return
        pose = cap.detect_pose(frame)
        if pose is None:
            self.marker_status.config(text="No markers detected.")
        else:
            self.marker_status.config(text="Pose OK — markers detected.")

    # ------------------------------------------------------------ Capture
    def _build_capture(self):
        f = ttk.Frame(self.nb, padding=12)
        self.nb.add(f, text="4. Capture")

        left = ttk.Frame(f)
        left.pack(side="left", fill="y", padx=(0, 8))
        ttk.Label(left, text="Simulation angle (deg)").pack(anchor="w")
        self.azimuth = tk.DoubleVar(value=0.0)
        ttk.Scale(left, from_=0, to=350, variable=self.azimuth,
                  length=180).pack(fill="x")
        ttk.Button(left, text="Capture view",
                   command=self.capture_view).pack(fill="x", pady=6)
        ttk.Label(left, text="Views captured:").pack(anchor="w")
        self.view_list = tk.Listbox(left, height=8, width=26)
        self.view_list.pack(fill="both", expand=True)

        self.cap_fig = Figure(figsize=(4, 5), facecolor="white")
        self.cap_ax = self.cap_fig.add_subplot(111)
        self.cap_ax.set_title("last view (image points)")
        self.cap_canvas = FigureCanvasTkAgg(self.cap_fig, master=f)
        self.cap_canvas.get_tk_widget().pack(side="left", fill="both", expand=True)

    def capture_view(self):
        if self.source.get() == "sim":
            if self.capturer is None:
                self.capturer = capture3d.SimCapturer(num_pixels=self.num_pixels.get())
                self.K, self.dist = self.capturer.K, self.capturer.dist
            self.capturer.set_view(self.azimuth.get())
            rvec, tvec = self.capturer.detect_pose()
        else:
            if self.K is None or self.board is None:
                messagebox.showwarning("Capture", "Finish Calibration and Markers first.")
                return
            self.capturer = capture3d.HardwareCapturer(
                self.K, self.dist, self.board, self.detector, self.camera_index.get())
            try:
                frame = self.capturer.grab()
            except Exception as e:  # noqa: BLE001
                messagebox.showerror("Camera", str(e))
                return
            pose = self.capturer.detect_pose(frame)
            if pose is None:
                messagebox.showwarning("Capture", "No markers visible — reposition.")
                return
            rvec, tvec = pose

        P = self.capturer.projection_for(rvec, tvec)
        self.say("Sweeping LEDs...")
        self.root.update_idletasks()
        try:
            obs = self.capturer.capture_sweep(
                self.pi_host.get(), self.pi_port.get(), self.num_pixels.get())
        except Exception as e:  # noqa: BLE001
            messagebox.showerror("Sweep failed", str(e))
            return
        self.session.add_view(P, obs)
        self.view_list.insert("end", f"view {self.session.num_views}: {len(obs)} LEDs")
        self._draw_view(obs)
        self.say(f"View {self.session.num_views} captured ({len(obs)} LEDs). "
                 f"Need >= 2 from different angles.")

    def _draw_view(self, obs):
        self.cap_ax.clear()
        self.cap_ax.set_title("last view (image points)")
        if obs:
            xs = [p[0] for p in obs.values()]
            ys = [p[1] for p in obs.values()]
            self.cap_ax.scatter(xs, ys, s=8)
            self.cap_ax.invert_yaxis()
            self.cap_ax.set_aspect("equal")
        self.cap_canvas.draw_idle()

    # --------------------------------------------------------- Reconstruct
    def _build_reconstruct(self):
        f = ttk.Frame(self.nb, padding=12)
        self.nb.add(f, text="5. Reconstruct")

        bar = ttk.Frame(f)
        bar.pack(side="top", fill="x")
        ttk.Button(bar, text="Reconstruct", command=self.reconstruct).pack(side="left")
        ttk.Button(bar, text=f"Save 3D ({config.COORDINATES_3D_FILE})",
                   command=self.save_3d).pack(side="left", padx=6)
        self.recon_status = ttk.Label(f, text="Capture >= 2 views, then reconstruct.")
        self.recon_status.pack(anchor="w", pady=6)

        self.recon_fig = Figure(figsize=(5, 5), facecolor="white")
        self.recon_ax = self.recon_fig.add_subplot(111, projection="3d")
        self.recon_canvas = FigureCanvasTkAgg(self.recon_fig, master=f)
        self.recon_canvas.get_tk_widget().pack(fill="both", expand=True)

    def reconstruct(self):
        if self.session.num_views < 2:
            messagebox.showwarning("Reconstruct", "Need at least 2 views.")
            return
        self.points = self.session.reconstruct(min_views=2)
        if not self.points:
            self.recon_status.config(text="No LEDs reconstructed — capture more views.")
            return
        errs = [e for _X, e in self.points.values()]
        self.recon_status.config(
            text=f"Reconstructed {len(self.points)} LEDs | "
                 f"mean reproj error {np.mean(errs):.2f}px")
        self._draw_3d()
        self.say("Reconstruction done. Drag the plot to rotate; then Save 3D.")

    def _draw_3d(self):
        self.recon_ax.clear()
        pts = np.array([X for X, _e in self.points.values()])
        self.recon_ax.scatter(pts[:, 0], pts[:, 1], pts[:, 2],
                              c=pts[:, 2], cmap="viridis", s=12)
        self.recon_ax.set_title("reconstructed tree (drag to rotate)")
        try:
            self.recon_ax.set_box_aspect((1, 1, 2))
        except Exception:  # older matplotlib
            pass
        self.recon_canvas.draw_idle()

    def save_3d(self):
        if not self.points:
            messagebox.showwarning("Save", "Reconstruct first.")
            return
        rows = self.session.save(config.COORDINATES_3D_FILE, self.points)
        self.say(f"Saved {len(rows)} LEDs to {config.COORDINATES_3D_FILE}.")
        messagebox.showinfo("Saved", f"Wrote {len(rows)} LEDs to "
                            f"{config.COORDINATES_3D_FILE}.")

    # ----------------------------------------------------------- helpers
    def _hw_capturer_for_preview(self):
        """A HardwareCapturer just for grabbing frames during setup steps."""
        if self.source.get() != "hardware":
            messagebox.showinfo("Hardware only", "This step needs the Hardware source.")
            return None
        if self.capturer is None or not isinstance(self.capturer,
                                                   capture3d.HardwareCapturer):
            self.capturer = capture3d.HardwareCapturer(
                self.K if self.K is not None else vision.approx_intrinsics(*self.image_size),
                self.dist if self.dist is not None else np.zeros(5),
                self.board, self.detector, self.camera_index.get())
        return self.capturer


def main():
    root = tk.Tk()
    Wizard(root)
    root.mainloop()


if __name__ == "__main__":
    main()
