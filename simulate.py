#!/usr/bin/env python3
"""Run any animation script on the laptop with simulated LED hardware.

    python simulate.py demo.py
    python simulate.py secuencias.py
    python simulate.py plotting7.py

It puts ``fakehw/`` ahead of the real ``board``/``neopixel`` on the import path,
so the target script runs unchanged and renders to a matplotlib window. Close the
window (or press Ctrl-C) to stop.
"""

import glob
import os
import runpy
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))


def _list_animations():
    # tools, libraries, UIs, and network servers — not standalone animations
    skip = {"simulate.py", "launcher.py", "studio.py", "config.py",
            "layout.py", "animations.py", "font5x7.py",
            "opencam.py", "clienttest.py", "capturascliente.py",
            "capturas.py", "servertest.py"}
    return sorted(
        os.path.basename(p)
        for p in glob.glob(os.path.join(ROOT, "*.py"))
        if os.path.basename(p) not in skip
        and not os.path.basename(p).startswith("plotting")  # offline plots
    )


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("Animation scripts you can simulate:")
        for name in _list_animations():
            print(f"  {name}")
        return

    target = sys.argv[1]
    if not os.path.isabs(target):
        target = os.path.join(ROOT, target)
    if not os.path.exists(target):
        sys.exit(f"No such file: {target}")

    # fakehw first so `import board` / `import neopixel` resolve to the fakes,
    # ROOT so the target and config.py import normally.
    sys.path.insert(0, ROOT)
    sys.path.insert(0, os.path.join(ROOT, "fakehw"))

    sys.argv = [target] + sys.argv[2:]
    try:
        runpy.run_path(target, run_name="__main__")
    except KeyboardInterrupt:
        print("\nSimulation stopped.")


if __name__ == "__main__":
    main()
