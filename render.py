# render.py — minimal deterministic raster engine (pure stdlib).
#
# A tiny framebuffer ("Sheet") plus a hand-built 5x7 pixel font and a
# hand-rolled PNG encoder. No network, no files read, no clock, no
# randomness: the same program always writes the same bytes.
#
# The font below was drawn for this entry: every glyph is seven rows of
# five cells, '#' = ink, '.' = empty. Uppercase only; lowercase input is
# folded to uppercase, unknown glyphs render as a blank cell.

import math
import struct
import zlib


# ---------------------------------------------------------------- font

_GLYPHS = {
    "A": (" ##  ", "#  # ", "#  # ", "#### ", "#  # ", "#  # ", "#  # "),
    "B": ("#### ", "#   #", "#   #", "#### ", "#   #", "#   #", "#### "),
    "C": (" ### ", "#    ", "#    ", "#    ", "#    ", "#    ", " ### "),
    "D": ("#### ", "#   #", "#   #", "#   #", "#   #", "#   #", "#### "),
    "E": ("#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#####"),
    "F": ("#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#    "),
    "G": (" ### ", "#    ", "#    ", "# ###", "#   #", "#   #", " ### "),
    "H": ("#   #", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"),
    "I": ("#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "#####"),
    "J": ("  ###", "   # ", "   # ", "   # ", "   # ", "#  # ", " ##  "),
    "K": ("#   #", "#  # ", "# #  ", "##   ", "# #  ", "#  # ", "#   #"),
    "L": ("#    ", "#    ", "#    ", "#    ", "#    ", "#    ", "#####"),
    "M": ("#   #", "## ##", "# # #", "# # #", "#   #", "#   #", "#   #"),
    "N": ("#   #", "##  #", "##  #", "# # #", "#  ##", "#  ##", "#   #"),
    "O": (" ### ", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "),
    "P": ("#### ", "#   #", "#   #", "#### ", "#    ", "#    ", "#    "),
    "Q": (" ### ", "#   #", "#   #", "#   #", "# # #", "#  # ", " ## #"),
    "R": ("#### ", "#   #", "#   #", "#### ", "# #  ", "#  # ", "#   #"),
    "S": (" ####", "#    ", "#    ", " ### ", "    #", "    #", "#### "),
    "T": ("#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "),
    "U": ("#   #", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "),
    "V": ("#   #", "#   #", "#   #", "#   #", "#   #", " # # ", "  #  "),
    "W": ("#   #", "#   #", "#   #", "# # #", "# # #", "## ##", "#   #"),
    "X": ("#   #", "#   #", " # # ", "  #  ", " # # ", "#   #", "#   #"),
    "Y": ("#   #", "#   #", " # # ", "  #  ", "  #  ", "  #  ", "  #  "),
    "Z": ("#####", "    #", "   # ", "  #  ", " #   ", "#    ", "#####"),
    "0": (" ### ", "#  ##", "# # #", "##  #", "#   #", "#   #", " ### "),
    "1": ("  #  ", " ##  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "),
    "2": (" ### ", "#   #", "    #", "   # ", "  #  ", " #   ", "#####"),
    "3": ("#### ", "    #", "    #", " ### ", "    #", "    #", "#### "),
    "4": ("   # ", "  ## ", " # # ", "#  # ", "#####", "   # ", "   # "),
    "5": ("#####", "#    ", "#### ", "    #", "    #", "#   #", " ### "),
    "6": (" ### ", "#    ", "#    ", "#### ", "#   #", "#   #", " ### "),
    "7": ("#####", "    #", "   # ", "  #  ", "  #  ", "  #  ", "  #  "),
    "8": (" ### ", "#   #", "#   #", " ### ", "#   #", "#   #", " ### "),
    "9": (" ### ", "#   #", "#   #", " ####", "    #", "    #", " ### "),
    " ": ("     ", "     ", "     ", "     ", "     ", "     ", "     "),
    ".": ("     ", "     ", "     ", "     ", "     ", " ##  ", " ##  "),
    ",": ("     ", "     ", "     ", "     ", " ##  ", " ##  ", " #   "),
    ":": ("     ", " ##  ", " ##  ", "     ", " ##  ", " ##  ", "     "),
    ";": ("     ", " ##  ", " ##  ", "     ", " ##  ", " ##  ", " #   "),
    "-": ("     ", "     ", "     ", "#####", "     ", "     ", "     "),
    "!": ("  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "     ", "  #  "),
    "?": (" ### ", "#   #", "    #", "   # ", "  #  ", "     ", "  #  "),
    "'": ("  #  ", "  #  ", "  #  ", "     ", "     ", "     ", "     "),
    '"': (" # # ", " # # ", " # # ", "     ", "     ", "     ", "     "),
    "(": ("   ##", "  #  ", " #   ", " #   ", " #   ", "  #  ", "   ##"),
    ")": ("##   ", "  #  ", "   # ", "   # ", "   # ", "  #  ", "##   "),
    "/": ("    #", "    #", "   # ", "  #  ", " #   ", "#    ", "#    "),
    "$": ("  #  ", " ####", "# #  ", " ### ", "  # #", "#### ", "  #  "),
    "%": ("##  #", "## # ", "   # ", "  #  ", " #   ", "# ## ", "#  ##"),
    "&": (" ##  ", "#  # ", "# #  ", " #   ", "# # #", "#  # ", " ## #"),
    "+": ("     ", "  #  ", "  #  ", " ### ", "  #  ", "  #  ", "     "),
    "=": ("     ", "     ", "#####", "     ", "#####", "     ", "     "),
    "*": ("     ", " # # ", " ### ", "#####", " ### ", " # # ", "     "),
    "_": ("     ", "     ", "     ", "     ", "     ", "     ", "#####"),
    "#": (" # # ", " # # ", "#####", " # # ", "#####", " # # ", " # # "),
    "@": (" ### ", "#   #", "# ###", "# # #", "# ###", "#    ", " ### "),
    "°": (" ##  ", "#  # ", " ##  ", "     ", "     ", "     ", "     "),
    "•": ("     ", "     ", " ### ", " ### ", " ### ", "     ", "     "),
    "✓": ("     ", "    #", "   # ", "# #  ", " #   ", "     ", "     "),
    "×": ("     ", "#   #", " # # ", "  #  ", " # # ", "#   #", "     "),
    "—": ("     ", "     ", "     ", "#####", "     ", "     ", "     "),
    "–": ("     ", "     ", "     ", "#####", "     ", "     ", "     "),
    "’": ("  #  ", "  #  ", "  #  ", "     ", "     ", "     ", "     "),
    "‘": ("  #  ", "  #  ", "  #  ", "     ", "     ", "     ", "     "),
}

_BLANK = ("     ",) * 7
_CELL_W = 6   # glyph advance in font units (5 px + 1 px gap)
_CELL_H = 8   # line height in font units (7 px + 1 px gap)


def glyph(ch):
    """Return the 7-row pattern for one character (uppercase-folded)."""
    return _GLYPHS.get(ch.upper(), _BLANK)


def text_width(text, scale=1):
    """Pixel width of `text` at `scale` (trailing gap included)."""
    return len(text) * _CELL_W * scale


def wrap(text, max_width, scale=1):
    """Greedy word wrap to pixel width; a single over-wide word is split.

    Returns a list of lines (possibly [''] for empty input). Never emits a
    line wider than max_width unless one glyph alone exceeds it.
    """
    if not text:
        return [""]
    words = text.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_width:
            cur = trial
            continue
        if cur:
            lines.append(cur)
            cur = ""
        # Word alone may still be too wide: hard-split it glyph by glyph.
        while text_width(word, scale) > max_width:
            take = max(1, max_width // (_CELL_W * scale))
            lines.append(word[:take])
            word = word[take:]
        cur = word
    if cur or not lines:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- sheet

class Sheet:
    """An RGB framebuffer with small drawing primitives."""

    def __init__(self, width, height, paper):
        self.w = width
        self.h = height
        self.buf = bytearray(paper) * (width * height)

    def px(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i:i + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.buf[i:i + len(row)] = row

    def frame(self, x, y, w, h, color, t=1):
        self.rect(x, y, w, t, color)
        self.rect(x, y + h - t, w, t, color)
        self.rect(x, y, t, h, color)
        self.rect(x + w - t, y, t, h, color)

    def hline(self, x, y, w, color, t=1):
        self.rect(x, y, w, t, color)

    def vline(self, x, y, h, color, t=1):
        self.rect(x, y, t, h, color)

    def line(self, x0, y0, x1, y1, color):
        """Bresenham line, clipped by px()."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.px(x0, y0, color)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, color):
        """Filled circle."""
        for yy in range(cy - r, cy + r + 1):
            dx = int((r * r - (yy - cy) ** 2) ** 0.5) if abs(yy - cy) <= r else -1
            if dx >= 0:
                self.rect(cx - dx, yy, 2 * dx + 1, 1, color)

    def ring(self, cx, cy, r, color, t=1):
        for k in range(t):
            rr = r - k
            steps = max(8, int(6.28 * rr))
            for s in range(steps):
                a = 2 * 3.141592653589793 * s / steps
                self.px(int(cx + rr * math.cos(a)), int(cy + rr * math.sin(a)), color)

    def tri(self, x0, y0, x1, y1, x2, y2, color):
        """Filled triangle via scanline fill."""
        pts = sorted(((x0, y0), (x1, y1), (x2, y2)), key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = pts
        if ay == cy:
            return
        for y in range(ay, cy + 1):
            xs = []
            for (px0, py0, px1, py1) in ((ax, ay, bx, by), (bx, by, cx, cy),
                                         (ax, ay, cx, cy)):
                if py0 == py1:
                    continue
                if min(py0, py1) <= y < max(py0, py1) or (y == cy and max(py0, py1) == cy):
                    t = (y - py0) / (py1 - py0)
                    xs.append(px0 + t * (px1 - px0))
            if len(xs) >= 2:
                xa, xb = int(min(xs)), int(max(xs))
                self.rect(xa, y, xb - xa + 1, 1, color)

    def poly(self, points, color):
        """Filled polygon (convex or concave) via scanline fill."""
        if len(points) < 3:
            return
        ys = [p[1] for p in points]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(points)
            for i in range(n):
                x0, y0 = points[i]
                x1, y1 = points[(i + 1) % n]
                if y0 == y1:
                    continue
                if min(y0, y1) <= y < max(y0, y1):
                    t = (y - y0) / (y1 - y0)
                    xs.append(x0 + t * (x1 - x0))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                xa, xb = int(xs[k]), int(xs[k + 1])
                self.rect(xa, y, xb - xa + 1, 1, color)

    # -- text ------------------------------------------------------------

    def text(self, x, y, s, scale, color):
        """Draw `s` at pixel (x, y); returns pixel x just past the text."""
        cx = x
        for ch in s:
            pat = glyph(ch)
            for row in range(7):
                bits = pat[row]
                for col in range(5):
                    if bits[col] == "#":
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, color)
            cx += _CELL_W * scale
        return cx

    def text_centred(self, cx, y, s, scale, color):
        x = cx - text_width(s, scale) // 2
        return self.text(x, y, s, scale, color)

    def para(self, x, y, s, max_width, scale, color, leading=None):
        """Wrapped paragraph; returns y just past the last line."""
        lh = leading if leading is not None else _CELL_H * scale + 2
        for line in wrap(s, max_width, scale):
            self.text(x, y, line, scale, color)
            y += lh
        return y


# ---------------------------------------------------------------- png

def write_png(sheet, path):
    """Encode the sheet as a PNG (filter 0 rows, zlib level 9)."""
    w, h = sheet.w, sheet.h
    raw = bytearray()
    stride = w * 3
    for y in range(h):
        raw.append(0)
        raw += sheet.buf[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(kind, data):
        c = struct.pack(">I", len(data)) + kind + data
        c += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return c

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", comp) + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)
    return len(png)
