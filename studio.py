#!/usr/bin/env python3
"""pino studio — one window with a live tree view plus animation controls.

    python studio.py

Pick an animation, type text and hit "Send to tree" for the text effects, and
switch between the captured (real) map and a synthetic cone. Rendering uses
blitting so the controls stay responsive.
"""

import tkinter as tk
from tkinter import ttk

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import animations
import config
import layout

COLORS = {
    "White": (255, 255, 255),
    "Red": (255, 0, 0),
    "Green": (0, 200, 0),
    "Blue": (0, 80, 255),
    "Gold": (255, 180, 0),
    "Magenta": (255, 0, 180),
    "Cyan": (0, 220, 220),
}

FPS_MS = 30
TEXT_ANIMS = (animations.ScrollingText, animations.LetterText)


class Studio:
    def __init__(self, root):
        self.root = root
        self.anim = None
        self._bg = None
        root.title("pino studio")

        main = ttk.Frame(root, padding=8)
        main.pack(fill="both", expand=True)

        controls = ttk.Frame(main)
        controls.pack(side="left", fill="y", padx=(0, 8))

        ttk.Label(controls, text="Animation").pack(anchor="w")
        self.anim_list = tk.Listbox(controls, height=len(animations.REGISTRY),
                                    exportselection=False)
        for name in animations.REGISTRY:
            self.anim_list.insert("end", name)
        self.anim_list.selection_set(0)
        self.anim_list.bind("<<ListboxSelect>>", lambda _e: self.select_anim())
        self.anim_list.pack(fill="x", pady=(0, 10))

        ttk.Label(controls, text="Text").pack(anchor="w")
        self.text_var = tk.StringVar(value="MERRY CHRISTMAS")
        entry = ttk.Entry(controls, textvariable=self.text_var, width=22)
        entry.pack(fill="x")
        entry.bind("<Return>", lambda _e: self.send_text())
        ttk.Button(controls, text="Send to tree",
                   command=self.send_text).pack(fill="x", pady=(4, 10))

        ttk.Label(controls, text="Color").pack(anchor="w")
        self.color_var = tk.StringVar(value="White")
        ttk.Combobox(controls, textvariable=self.color_var, values=list(COLORS),
                     state="readonly").pack(fill="x", pady=(0, 10))
        self.color_var.trace_add("write", lambda *_a: self.apply_params())

        ttk.Label(controls, text="Layout").pack(anchor="w")
        self.layout_var = tk.StringVar(value="captured")
        for val, lbl in (("captured", "Captured (real map)"),
                         ("synthetic", "Synthetic cone")):
            ttk.Radiobutton(controls, text=lbl, value=val,
                            variable=self.layout_var,
                            command=self.build_display).pack(anchor="w")

        ttk.Label(controls, text="Text size (Scrolling)").pack(anchor="w", pady=(10, 0))
        self.text_size = tk.DoubleVar(value=0.28)
        ttk.Scale(controls, from_=0.15, to=0.6, variable=self.text_size,
                  command=lambda _e: self.apply_params()).pack(fill="x")

        ttk.Label(controls, text="Speed").pack(anchor="w")
        self.speed = tk.DoubleVar(value=0.4)
        ttk.Scale(controls, from_=0.05, to=1.5, variable=self.speed,
                  command=lambda _e: self.apply_params()).pack(fill="x")

        ttk.Label(controls, text="Brightness").pack(anchor="w")
        self.brightness = tk.DoubleVar(value=0.6)
        ttk.Scale(controls, from_=0.05, to=1.0,
                  variable=self.brightness).pack(fill="x")

        self.fig = Figure(figsize=(4.5, 7), facecolor="black")
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=main)
        self.canvas.get_tk_widget().pack(side="left", fill="both", expand=True)
        self.canvas.mpl_connect("resize_event", lambda _e: self._invalidate_bg())

        self.frame = 0
        self.build_display()
        self._tick()

    # --- display / animation setup ---

    def build_display(self):
        """(Re)create the LED scatter for the current layout."""
        coords = layout.positions(config.NUM_PIXELS, self.layout_var.get(),
                                  config.COORDINATES_FILE)
        self.norm = animations.normalize(coords)
        self.ax.clear()
        self.ax.set_facecolor("black")
        self.ax.set_aspect("equal")
        self.ax.axis("off")
        self.ax.margins(0.05)
        xs = [c[0] for c in coords]
        ys = [c[1] for c in coords]
        self.scatter = self.ax.scatter(
            xs, ys, s=45, c=[(0.0, 0.0, 0.0)] * len(coords), edgecolors="none"
        )
        self._invalidate_bg()
        self._make_anim(reset=False)

    def select_anim(self):
        self._make_anim(reset=True)

    def send_text(self):
        if isinstance(self.anim, TEXT_ANIMS):
            self.anim.set_text(self.text_var.get())  # smooth, no restart
        else:
            self._make_anim(reset=True)

    def _make_anim(self, reset):
        sel = self.anim_list.curselection()
        name = self.anim_list.get(sel[0] if sel else 0)
        cls = animations.REGISTRY[name]
        color = COLORS[self.color_var.get()]
        if cls is animations.ScrollingText:
            self.anim = cls(self.norm, text=self.text_var.get(), color=color,
                            speed=self.speed.get(),
                            text_height=self.text_size.get())
        elif cls is animations.LetterText:
            self.anim = cls(self.norm, text=self.text_var.get(), color=color,
                            speed=self.speed.get())
        elif cls in (animations.Solid, animations.Twinkle):
            self.anim = cls(self.norm, color=color)
        else:
            self.anim = cls(self.norm)
        if reset:
            self.frame = 0

    def apply_params(self):
        """Update the live animation's parameters without rebuilding it."""
        a = self.anim
        if a is None:
            return
        if hasattr(a, "color"):
            a.color = COLORS[self.color_var.get()]
        if hasattr(a, "speed"):
            a.speed = self.speed.get()
        if hasattr(a, "text_height"):
            a.text_height = self.text_size.get()

    # --- render loop (blitted) ---

    def _invalidate_bg(self):
        self._bg = None

    def _tick(self):
        if self.anim is not None:
            b = self.brightness.get()
            colors = self.anim.render(self.frame)
            self.scatter.set_color([
                (r / 255 * b, g / 255 * b, bl / 255 * b) for (r, g, bl) in colors
            ])
            if self._bg is None:
                self.canvas.draw()
                self._bg = self.canvas.copy_from_bbox(self.ax.bbox)
            else:
                self.canvas.restore_region(self._bg)
                self.ax.draw_artist(self.scatter)
                self.canvas.blit(self.ax.bbox)
                self.canvas.flush_events()
            self.frame += 1
        self.root.after(FPS_MS, self._tick)


def main():
    root = tk.Tk()
    Studio(root)
    root.mainloop()


if __name__ == "__main__":
    main()
