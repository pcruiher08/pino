#!/usr/bin/env python3
"""Interactive launcher for the pino animation simulator.

Pick an animation from the list, choose whether to lay the LEDs out as the real
captured map or a generated cone, and Play it. Each animation runs in its own
process (via simulate.py) and renders to a matplotlib window.

    python launcher.py
"""

import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk

import simulate

ROOT = os.path.dirname(os.path.abspath(__file__))
ANIMATIONS = simulate._list_animations()


class Launcher:
    def __init__(self, root):
        self.root = root
        self.proc = None
        self.current = None

        root.title("pino — animation launcher")
        root.minsize(280, 360)
        root.protocol("WM_DELETE_WINDOW", self.on_close)

        frame = ttk.Frame(root, padding=10)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Animation").pack(anchor="w")
        self.listbox = tk.Listbox(frame, height=12, exportselection=False)
        for name in ANIMATIONS:
            self.listbox.insert("end", name)
        if ANIMATIONS:
            self.listbox.selection_set(0)
        self.listbox.bind("<Double-Button-1>", lambda _e: self.play())
        self.listbox.pack(fill="both", expand=True, pady=(0, 10))

        ttk.Label(frame, text="LED layout").pack(anchor="w")
        self.layout = tk.StringVar(value="captured")
        row = ttk.Frame(frame)
        row.pack(anchor="w", pady=(0, 10))
        ttk.Radiobutton(row, text="Captured (real map)", value="captured",
                        variable=self.layout, command=self._on_layout).pack(side="left")
        ttk.Radiobutton(row, text="Synthetic cone", value="synthetic",
                        variable=self.layout, command=self._on_layout).pack(side="left")

        buttons = ttk.Frame(frame)
        buttons.pack(fill="x")
        ttk.Button(buttons, text="▶ Play", command=self.play).pack(side="left", expand=True, fill="x")
        ttk.Button(buttons, text="■ Stop", command=self.stop).pack(side="left", expand=True, fill="x")

        self.status = ttk.Label(frame, text="Ready", foreground="gray")
        self.status.pack(anchor="w", pady=(10, 0))

        self._poll()

    def play(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        anim = ANIMATIONS[sel[0]]
        self.stop()
        env = os.environ.copy()
        env["PINO_SIM_LAYOUT"] = self.layout.get()
        self.proc = subprocess.Popen(
            [sys.executable, os.path.join(ROOT, "simulate.py"), anim], env=env
        )
        self.current = anim
        self.status.config(text=f"Playing {anim}  ({self.layout.get()})")

    def stop(self):
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.proc.kill()
        self.proc = None
        self.current = None
        self.status.config(text="Stopped")

    def _on_layout(self):
        # Restart the running animation so the layout change takes effect now.
        if self.current:
            anim = self.current
            self.stop()
            idx = ANIMATIONS.index(anim)
            self.listbox.selection_clear(0, "end")
            self.listbox.selection_set(idx)
            self.play()

    def _poll(self):
        # Reflect the window being closed by the user.
        if self.proc and self.proc.poll() is not None:
            self.proc = None
            self.current = None
            self.status.config(text="Ready")
        self.root.after(400, self._poll)

    def on_close(self):
        self.stop()
        self.root.destroy()


def main():
    if not ANIMATIONS:
        sys.exit("No animations found.")
    root = tk.Tk()
    Launcher(root)
    root.mainloop()


if __name__ == "__main__":
    main()
