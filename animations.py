"""Frame-based LED animations driven by normalized tree positions.

Each animation is built from `leds` — a list of (nx, ny) positions normalized to
[0, 1] — and `render(frame)` returns a list of (r, g, b) tuples, one per LED.

Used by the studio UI (studio.py) and by scrolltext.py, which pushes the same
frames to the real or simulated strip.
"""

import colorsys
import random

from font5x7 import FONT, HEIGHT, WIDTH, text_columns


def normalize(coords):
    """Map raw (x, y) into (nx, ny), aspect preserved.

    ny spans [0, 1] over the tree height; nx uses the *same* scale, so a narrow
    tree gives nx in [0, W/H]. Keeping one scale lets text cells stay square
    instead of being stretched to the tree's height.
    """
    xs = [c[0] for c in coords]
    ys = [c[1] for c in coords]
    minx = min(xs)
    miny, maxy = min(ys), max(ys)
    dy = (maxy - miny) or 1.0
    return [((x - minx) / dy, (y - miny) / dy) for x, y in coords]


def _hsv(h, s=1.0, v=1.0):
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return (int(r * 255), int(g * 255), int(b * 255))


class Animation:
    def __init__(self, leds):
        self.leds = leds
        self.n = len(leds)

    def render(self, frame):
        raise NotImplementedError


class Solid(Animation):
    def __init__(self, leds, color=(255, 255, 255)):
        super().__init__(leds)
        self.color = color

    def render(self, frame):
        return [self.color] * self.n


class Rainbow(Animation):
    def render(self, frame):
        t = frame * 0.01
        return [_hsv((ny + t) % 1.0) for (_nx, ny) in self.leds]


class Twinkle(Animation):
    def __init__(self, leds, color=(255, 255, 255), base=(0, 25, 0), density=0.08):
        super().__init__(leds)
        self.color = color
        self.base = base
        self.k = max(1, int(self.n * density))

    def render(self, frame):
        rng = random.Random(frame // 4)  # hold each sparkle set for a few frames
        out = [self.base] * self.n
        for i in rng.sample(range(self.n), self.k):
            out[i] = self.color
        return out


class ScrollingText(Animation):
    """Scroll text across the tree, right to left.

    Text occupies a horizontal band `text_height` tall (a fraction of the tree
    height) centered at `text_y`. Font cells are kept square — using the
    aspect-preserving coords from `normalize` — so letters look right instead of
    being stretched over the whole tree. Smaller `text_height` => smaller letters
    and more of them visible at once.
    """

    def __init__(self, leds, text="MERRY CHRISTMAS", color=(255, 255, 255),
                 bg=(0, 0, 0), speed=0.4, text_height=0.28, text_y=0.5):
        super().__init__(leds)
        self.color = color
        self.bg = bg
        self.speed = speed
        self.text_height = text_height
        self.text_y = text_y
        self.max_nx = max((nx for nx, _ny in leds), default=1.0)
        self.set_text(text)

    def set_text(self, text):
        self.cols = text_columns(text or " ")

    def render(self, frame):
        h = self.text_height
        pitch = h / (HEIGHT - 1)          # square cell size in normalized units
        width_cells = self.max_nx / pitch  # font columns spanning the tree width
        cols, ncols = self.cols, len(self.cols)
        span = ncols + width_cells
        pos = (frame * self.speed) % span - width_cells
        y_top = self.text_y + h / 2
        color, bg = self.color, self.bg
        out = []
        for (nx, ny) in self.leds:
            frac = (y_top - ny) / h
            if 0.0 <= frac <= 1.0:
                row = int(round(frac * (HEIGHT - 1)))
                ci = int(nx / pitch + pos)
                out.append(color if 0 <= ci < ncols and cols[ci][row] else bg)
            else:
                out.append(bg)
        return out


class LetterText(Animation):
    """Show the message one big letter at a time, each filling the whole tree.

    On a narrow tree this reads far better than scrolling: every letter uses the
    full LED resolution instead of being squeezed into a ~2-character window.
    Spaces become brief blanks. `speed` controls how fast letters advance.
    """

    def __init__(self, leds, text="MERRY CHRISTMAS", color=(255, 255, 255),
                 bg=(0, 0, 0), speed=0.4, fill=0.92):
        super().__init__(leds)
        self.color = color
        self.bg = bg
        self.speed = speed
        self.fill = fill
        self.max_nx = max((nx for nx, _ny in leds), default=1.0)
        self.set_text(text)

    def set_text(self, text):
        self.chars = list((text or " ").upper())

    def render(self, frame):
        frames_per_letter = max(4, int(round(16 * 0.4 / max(self.speed, 1e-3))))
        ch = self.chars[(frame // frames_per_letter) % len(self.chars)]
        glyph = FONT.get(ch)
        if glyph is None or ch == " ":
            return [self.bg] * self.n
        # Largest square cell that fits the glyph in both axes, then center it.
        s = min(self.max_nx / WIDTH, 1.0 / HEIGHT) * self.fill
        x0 = (self.max_nx - WIDTH * s) / 2
        y_top = (1.0 + HEIGHT * s) / 2
        color, bg = self.color, self.bg
        out = []
        for (nx, ny) in self.leds:
            col = int((nx - x0) / s)
            row = int((y_top - ny) / s)
            on = 0 <= col < WIDTH and 0 <= row < HEIGHT and glyph[row][col] == "#"
            out.append(color if on else bg)
        return out


# Display name -> class. Order controls the studio's list.
REGISTRY = {
    "Letters": LetterText,
    "Scrolling Text": ScrollingText,
    "Rainbow": Rainbow,
    "Twinkle": Twinkle,
    "Solid": Solid,
}
