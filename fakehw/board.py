"""Laptop stand-in for Adafruit's ``board`` module.

Any attribute access (e.g. ``board.D18``) just returns the pin name, so animation
scripts written for the Raspberry Pi import cleanly on a laptop.
"""


def __getattr__(name):
    return name
