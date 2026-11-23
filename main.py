#!/usr/bin/env python3
"""Monday 23 November 2026 - the world in one image.

Draws a one-page newspaper front page that sums up the day's world news
and writes it to $MAKEFUN_OUTPUT_DIR/entry.png (default /output).

Pure standard library: the PNG is encoded by hand (zlib + struct) and
every shape and letter is rasterised by this file - no fonts, no PIL,
no network, no randomness, so two runs write identical bytes.

Stories (all first reported on 22-23 November 2026):
  - Strait of Hormuz: Iranian attacks on shipping at their highest
    level since the US-Iran war began; three tankers struck since
    Friday; Trump favours an economic squeeze over new strikes; the
    US blockade of Iran enters day 130. (CNN, 22 Nov)
  - Dymer, Kyiv region: a Russian drone collapses part of a
    five-storey block; one dead, 14 missing, nine evacuated.
    (Reuters, 22 Nov)
  - COP31 in Antalya ends with no deal: the final draft dropped any
    mention of fossil fuels and the EU rejected it. (AFP, 23 Nov)
  - Banten, Indonesia: a candy factory fire kills 3 and leaves about
    50 workers missing; seven body bags recovered. (Reuters, 22 Nov)
  - Lisbon: thousands march as anger over living costs boils over.
  - South Sudan: 24 civilians killed in fresh violence. (AFP, 22 Nov)
Ticker: Nepal PM in Delhi for talks with Modi; South Korea's
education minister quits over an AI exam-cheating scandal; the UN
agrees to keep negotiating on lethal AI weapons; Kim Jong Un says
North Korea seeks security, not supremacy.
"""

import os
import struct
import zlib
from math import sqrt

W, H = 1024, 1024

# ---- palette ---------------------------------------------------------
PAPER = (246, 241, 230)
INK = (24, 32, 54)
INK_SOFT = (58, 70, 96)
RED = (178, 38, 30)
RED_DARK = (132, 26, 20)
TEAL = (14, 110, 104)
GOLD = (198, 150, 40)
SKY = (176, 212, 233)
SKY_PALE = (216, 233, 242)
SEA = (24, 96, 124)
SEA_DARK = (16, 68, 94)
ORANGE = (232, 116, 28)
YELLOW = (244, 196, 66)
GREEN = (46, 125, 70)
GREY = (120, 124, 128)
GREY_DARK = (88, 92, 96)
GREY_LIGHT = (208, 206, 198)
WHITE = (255, 255, 255)
CREAM = (232, 222, 198)
SMOKE = (150, 148, 142)

# ---- 5x7 bitmap font, authored here: each glyph is 7 rows of 5 bits --
_GLYPHS = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    "*": ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    "[": ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    "]": ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
}
FONT = {ch: tuple(int(row, 2) for row in rows) for ch, rows in _GLYPHS.items()}
CHAR_W = 6  # 5 px glyph + 1 px gap, before scaling


class Canvas:
    """An RGB framebuffer with small filled-shape helpers."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(w * h * 3)
        self.fill(bg)

    def fill(self, color):
        r, g, b = color
        self.buf[0::3] = bytes([r]) * (self.w * self.h)
        self.buf[1::3] = bytes([g]) * (self.w * self.h)
        self.buf[2::3] = bytes([b]) * (self.w * self.h)

    def px(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i], self.buf[i + 1], self.buf[i + 2] = color

    def rect(self, x, y, w, h, color):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            span = (x1 - x0) * 3
            self.buf[base:base + span] = bytes(color) * (x1 - x0)

    def hline(self, x, y, w, color):
        self.rect(x, y, w, 1, color)

    def vline(self, x, y, h, color):
        self.rect(x, y, 1, h, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.rect(x0 - thick // 2, y0 - thick // 2, thick, thick, color)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            dx = int(sqrt(max(0, r * r - (yy - cy) ** 2)))
            self.rect(cx - dx, yy, 2 * dx + 1, 1, color)

    def ring(self, cx, cy, r, color, thick=2):
        for yy in range(cy - r - thick, cy + r + thick + 1):
            for xx in range(cx - r - thick, cx + r + thick + 1):
                d = sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
                if r - thick <= d <= r:
                    self.px(xx, yy, color)

    def poly(self, pts, color):
        """Scanline fill of a simple polygon."""
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    t = (y - y0) / (y1 - y0)
                    xs.append(x0 + t * (x1 - x0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.rect(int(xs[i]), y, max(1, int(xs[i + 1]) - int(xs[i])), 1, color)

    def tri(self, a, b, c, color):
        self.poly([a, b, c], color)

    # ---- text --------------------------------------------------------
    def text(self, s, x, y, scale, color):
        s = s.upper()
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[" "])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits & (1 << (4 - col)):
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, color)
            cx += CHAR_W * scale
        return cx

    def text_w(self, s, scale):
        return len(s) * CHAR_W * scale

    def text_center(self, s, cx, y, scale, color):
        self.text(s, cx - self.text_w(s, scale) // 2, y, scale, color)

    def wrap(self, text, max_w, scale):
        """Greedy word wrap; returns a list of lines."""
        lines, cur = [], ""
        for word in text.split(" "):
            trial = word if not cur else cur + " " + word
            if self.text_w(trial, scale) <= max_w:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines


def encode_png(canvas):
    """Hand-rolled PNG: filter 0 on every row, zlib level 9."""
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)
        raw += canvas.buf[y * stride:(y + 1) * stride]
    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out
    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


# ---- illustrations ---------------------------------------------------
# Each draws inside the rectangle (x, y, w, h) given to it.

def art_hormuz(cv, x, y, w, h):
    """A tanker burning in the Strait of Hormuz under a pale sun."""
    cv.rect(x, y, w, h, SKY_PALE)
    cv.circle(x + w - 52, y + 34, 22, YELLOW)
    cv.circle(x + w - 52, y + 34, 16, GOLD)
    cv.rect(x, y + h - 78, w, 78, SEA)
    cv.rect(x, y + h - 78, w, 6, SEA_DARK)
    cv.rect(x, y + h - 52, w, 4, SEA_DARK)
    cv.rect(x, y + h - 26, w, 4, SEA_DARK)
    # tanker hull with a pointed bow
    hx, hy = x + 24, y + h - 118
    cv.poly([(hx, hy + 26), (hx + 34, hy), (hx + w - 84, hy),
             (hx + w - 52, hy + 26), (hx + w - 52, hy + 44),
             (hx, hy + 44)], INK)
    cv.rect(hx + 8, hy - 30, 46, 30, RED)
    cv.rect(hx + 60, hy - 30, 46, 30, TEAL)
    cv.rect(hx + 112, hy - 30, 46, 30, GOLD)
    cv.rect(hx + 164, hy - 30, 46, 30, GREY_DARK)
    cv.rect(hx + 216, hy - 46, 26, 46, WHITE)
    cv.rect(hx + 216, hy - 46, 26, 8, RED)
    # flames above the mid-deck
    fx = hx + 130
    cv.tri((fx, hy - 28), (fx + 14, hy - 78), (fx + 30, hy - 28), ORANGE)
    cv.tri((fx + 22, hy - 28), (fx + 34, hy - 64), (fx + 48, hy - 28), YELLOW)
    cv.tri((fx + 42, hy - 28), (fx + 52, hy - 56), (fx + 64, hy - 28), ORANGE)
    # smoke puffs drifting up
    cv.circle(fx + 20, hy - 92, 12, SMOKE)
    cv.circle(fx + 38, hy - 108, 15, GREY_LIGHT)
    cv.circle(fx + 58, hy - 122, 12, SMOKE)
    # distant second ship and a gull
    cv.rect(x + w - 120, y + h - 96, 74, 10, INK_SOFT)
    cv.rect(x + w - 104, y + h - 106, 12, 10, INK_SOFT)
    cv.line(x + 40, y + 26, x + 52, y + 20, INK_SOFT, 2)
    cv.line(x + 52, y + 20, x + 64, y + 26, INK_SOFT, 2)


def art_kyiv(cv, x, y, w, h):
    """A five-storey block, its right half collapsed, a drone above."""
    cv.rect(x, y, w, h, SKY_PALE)
    cv.circle(x + 34, y + 24, 14, YELLOW)
    bx, by = x + 18, y + h - 78
    bw, bh = 150, 78
    cv.rect(bx, by, bw, bh, GREY_LIGHT)
    cv.rect(bx, by, bw, 6, GREY_DARK)
    for r in range(4):
        for c in range(5):
            cv.rect(bx + 10 + c * 28, by + 14 + r * 16, 14, 9,
                    INK_SOFT if (r + c) % 2 else GOLD)
    # collapsed right section: jagged ruin and rubble
    rx = bx + bw
    cv.poly([(rx, by), (rx + 66, by + 8), (rx + 58, by + 30),
             (rx + 70, by + 52), (rx + 52, by + bh), (rx, by + bh)],
            GREY_DARK)
    cv.tri((rx + 4, by + bh), (rx + 26, by + bh - 22), (rx + 48, by + bh), GREY)
    cv.tri((rx + 30, by + bh), (rx + 52, by + bh - 16), (rx + 74, by + bh), SMOKE)
    cv.rect(rx + 8, by + 18, 10, 7, ORANGE)
    cv.rect(rx + 8, by + 34, 8, 6, YELLOW)
    # quadcopter drone with four rotors
    dx, dy = x + w - 62, y + 30
    cv.rect(dx - 10, dy - 5, 20, 10, INK)
    cv.line(dx - 22, dy - 8, dx - 2, dy - 2, INK, 2)
    cv.line(dx + 2, dy - 2, dx + 22, dy - 8, INK, 2)
    cv.line(dx - 22, dy + 8, dx - 2, dy + 2, INK, 2)
    cv.line(dx + 2, dy + 2, dx + 22, dy + 8, INK, 2)
    for px_, py_ in ((dx - 24, dy - 9), (dx + 24, dy - 9),
                     (dx - 24, dy + 9), (dx + 24, dy + 9)):
        cv.hline(px_ - 8, py_, 17, INK)
    cv.circle(dx, dy + 12, 2, RED)


def art_cop31(cv, x, y, w, h):
    """A globe with a crack, and a red NO DEAL stamp."""
    cv.rect(x, y, w, h, SKY_PALE)
    cx, cy, r = x + 66, y + h // 2 + 4, 44
    cv.circle(cx, cy, r, TEAL)
    cv.circle(cx, cy, r - 6, SEA)
    # latitude and longitude arcs
    cv.hline(cx - r + 8, cy - 20, 2 * r - 16, SKY)
    cv.hline(cx - r + 4, cy + 18, 2 * r - 8, SKY)
    cv.vline(cx, cy - r + 4, 2 * r - 8, SKY)
    cv.line(cx - 26, cy - 34, cx + 26, cy + 34, SKY, 2)
    cv.line(cx + 26, cy - 34, cx - 26, cy + 34, SKY, 2)
    # the crack: a jagged red line across the globe
    cv.line(cx - 30, cy - 26, cx - 10, cy - 8, RED, 3)
    cv.line(cx - 10, cy - 8, cx - 22, cy + 10, RED, 3)
    cv.line(cx - 22, cy + 10, cx + 2, cy + 26, RED, 3)
    cv.line(cx + 2, cy + 26, cx + 18, cy + 38, RED, 3)
    # smokestacks on the right
    sx = x + w - 96
    cv.rect(sx, y + h - 66, 16, 66, GREY_DARK)
    cv.rect(sx + 24, y + h - 54, 16, 54, GREY_DARK)
    cv.rect(sx + 48, y + h - 74, 16, 74, GREY_DARK)
    cv.circle(sx + 8, y + h - 78, 8, SMOKE)
    cv.circle(sx + 32, y + h - 66, 8, SMOKE)
    cv.circle(sx + 56, y + h - 86, 9, SMOKE)
    # NO DEAL stamp
    tx, ty = x + w - 150, y + 12
    cv.rect(tx, ty, 132, 30, WHITE)
    cv.rect(tx, ty, 132, 30, RED)
    cv.rect(tx + 3, ty + 3, 126, 24, WHITE)
    cv.text("NO DEAL", tx + 12, ty + 9, 2, RED)


def art_factory(cv, x, y, w, h):
    """A factory with a sawtooth roof, flames and smoke."""
    cv.rect(x, y, w, h, SKY_PALE)
    fx, fy = x + 16, y + h - 62
    fw = w - 32
    cv.rect(fx, fy, fw, 62, GREY_DARK)
    # sawtooth roof
    for i in range(4):
        tx0 = fx + i * (fw // 4)
        cv.tri((tx0, fy), (tx0 + fw // 8, fy - 20), (tx0 + fw // 4, fy), GREY)
    cv.rect(fx + 10, fy + 14, 18, 12, GOLD)
    cv.rect(fx + 40, fy + 14, 18, 12, GOLD)
    cv.rect(fx + 70, fy + 14, 18, 12, GOLD)
    cv.rect(fx + 100, fy + 14, 18, 12, GOLD)
    cv.rect(fx + 130, fy + 14, 18, 12, GOLD)
    # flames licking the roofline
    for i, fx2 in enumerate((fx + 30, fx + 90, fx + 150)):
        cv.tri((fx2, fy), (fx2 + 10, fy - 34 - 6 * (i % 2)),
               (fx2 + 20, fy), ORANGE)
        cv.tri((fx2 + 5, fy), (fx2 + 11, fy - 20), (fx2 + 16, fy), YELLOW)
    # smoke columns
    cv.circle(fx + 44, fy - 44, 12, SMOKE)
    cv.circle(fx + 66, fy - 62, 14, GREY_LIGHT)
    cv.circle(fx + 150, fy - 48, 12, SMOKE)
    cv.circle(fx + 168, fy - 66, 13, GREY_LIGHT)


def art_lisbon(cv, x, y, w, h):
    """A crowd marching with placards under a low sun."""
    cv.rect(x, y, w, h, SKY_PALE)
    cv.circle(x + w // 2, y + 20, 15, GOLD)
    cv.circle(x + w // 2, y + 20, 10, YELLOW)
    # back row of heads
    for i in range(7):
        hx = x + 22 + i * 38
        cv.circle(hx, y + 52, 9, INK_SOFT)
        cv.rect(hx - 9, y + 62, 18, 22, GREY_DARK)
    # front row, bigger
    for i in range(6):
        hx = x + 34 + i * 44
        cv.circle(hx, y + h - 34, 11, INK)
        cv.rect(hx - 11, y + h - 22, 22, 22, RED if i % 2 else TEAL)
    # placards on sticks
    cv.rect(x + 30, y + 18, 52, 24, WHITE)
    cv.rect(x + 30, y + 18, 52, 24, INK)
    cv.text("COST", x + 38, y + 25, 1, RED)
    cv.vline(x + 56, y + 42, 14, INK)
    cv.rect(x + w - 96, y + 22, 62, 24, WHITE)
    cv.rect(x + w - 96, y + 22, 62, 24, INK)
    cv.text("ENOUGH", x + w - 90, y + 29, 1, RED)
    cv.vline(x + w - 66, y + 46, 12, INK)


def art_sudan(cv, x, y, w, h):
    """A simplified Africa with a red marker over the east."""
    cv.rect(x, y, w, h, SKY_PALE)
    # rough Africa silhouette, hand-placed points
    pts = [(x + 108, y + 8), (x + 150, y + 6), (x + 176, y + 18),
           (x + 182, y + 44), (x + 168, y + 62), (x + 150, y + 66),
           (x + 138, y + 82), (x + 128, y + 104), (x + 112, y + 118),
           (x + 96, y + 100), (x + 84, y + 76), (x + 66, y + 58),
           (x + 62, y + 34), (x + 78, y + 16)]
    cv.poly(pts, CREAM)
    for i in range(len(pts)):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % len(pts)]
        cv.line(x0, y0, x1, y1, GOLD, 2)
    # marker star over the east (South Sudan area)
    mx, my = x + 158, y + 46
    cv.circle(mx, my, 9, RED)
    cv.circle(mx, my, 4, WHITE)
    cv.circle(mx, my, 2, RED)
    # small tent camp marks
    for tx, ty in ((x + 96, y + 70), (x + 112, y + 78)):
        cv.tri((tx, ty), (tx + 6, ty - 10), (tx + 12, ty), INK_SOFT)
    cv.text("SUDAN", x + 116, y + h - 16, 1, INK_SOFT)


# ---- page layout -----------------------------------------------------

def panel(cv, x, y, w, h, accent, kicker, headline, body, art, art_h):
    """One story panel: illustration on top, kicker, headline, body."""
    cv.rect(x, y, w, h, WHITE)
    cv.rect(x, y, w, h, INK)  # border via four thin rects below
    cv.rect(x + 2, y + 2, w - 4, h - 4, WHITE)
    cv.rect(x, y, w, 6, accent)
    art(cv, x + 8, y + 12, w - 16, art_h)
    ty = y + 12 + art_h + 8
    cv.text(kicker, x + 12, ty, 1, accent)
    ty += 14
    for line in cv.wrap(headline, w - 24, 2):
        cv.text(line, x + 12, ty, 2, INK)
        ty += 17
    ty += 3
    for line in cv.wrap(body, w - 24, 1):
        cv.text(line, x + 12, ty, 1, INK_SOFT)
        ty += 11


def draw_page():
    cv = Canvas(W, H, PAPER)
    # outer frame
    cv.rect(0, 0, W, 4, INK)
    cv.rect(0, H - 4, W, 4, INK)
    cv.rect(0, 0, 4, H, INK)
    cv.rect(W - 4, 0, 4, H, INK)

    # ---- masthead ----------------------------------------------------
    cv.rect(20, 20, 984, 96, INK)
    cv.rect(20, 20, 984, 4, RED)
    cv.text_center("THE WORLD TODAY", 512, 32, 4, WHITE)
    cv.text_center("MONDAY 23 NOVEMBER 2026  -  ONE DAY IN THE NEWS",
                   512, 74, 2, GOLD)
    cv.hline(36, 100, 952, RED)

    # ---- lead story: the Gulf ---------------------------------------
    lx, ly, lw, lh = 20, 128, 984, 268
    cv.rect(lx, ly, lw, lh, WHITE)
    cv.rect(lx, ly, lw, 6, RED)
    cv.rect(lx, ly, lw, lh, INK)
    cv.rect(lx + 2, ly + 2, lw - 4, lh - 4, WHITE)
    cv.rect(lx, ly, lw, 6, RED)
    cv.text("THE GULF  -  LEAD STORY", lx + 16, ly + 18, 1, RED)
    ty = ly + 40
    for line in cv.wrap("HORMUZ ATTACKS AT HIGHEST LEVEL SINCE WAR BEGAN",
                        500, 3):
        cv.text(line, lx + 16, ty, 3, INK)
        ty += 24
    ty += 6
    lead_body = [
        "THREE TANKERS STRUCK SINCE FRIDAY AS TEHRAN",
        "PRESSES ITS GRIP ON THE VITAL WATERWAY.",
        "TRUMP FAVOURS AN ECONOMIC SQUEEZE OVER",
        "NEW STRIKES; THE US BLOCKADE ENTERS DAY 130.",
    ]
    for line in lead_body:
        cv.text(line, lx + 16, ty, 2, INK_SOFT)
        ty += 19
    ty += 6
    cv.text("SOURCE: CNN, 22 NOV", lx + 16, ty, 1, GREY)
    art_hormuz(cv, lx + 540, ly + 16, 428, 236)

    # ---- second row: Kyiv and COP31 ---------------------------------
    panel(cv, 20, 408, 484, 232, INK, "UKRAINE",
          "14 MISSING AFTER DRONE HITS FLATS NEAR KYIV",
          "A RUSSIAN DRONE COLLAPSED PART OF A FIVE-STOREY BLOCK "
          "IN DYMER; ONE DEAD, NINE RESCUED.",
          art_kyiv, 84)
    panel(cv, 520, 408, 484, 232, TEAL, "CLIMATE  -  ANTALYA",
          "COP31 ENDS WITH NO DEAL ON FOSSIL FUELS",
          "TALKS COLLAPSE AFTER THE FINAL DRAFT DROPPED ANY "
          "MENTION OF FOSSIL FUELS; THE EU SAID NO.",
          art_cop31, 84)

    # ---- third row: Indonesia, Lisbon, South Sudan -------------------
    panel(cv, 20, 652, 320, 232, ORANGE, "INDONESIA",
          "50 MISSING AFTER CANDY FACTORY FIRE",
          "BLAZE RIPS THROUGH A THREE-STOREY PLANT IN "
          "BANTEN; SEVEN BODY BAGS RECOVERED.",
          art_factory, 80)
    panel(cv, 352, 652, 320, 232, RED, "PORTUGAL",
          "THOUSANDS MARCH IN LISBON OVER LIVING COSTS",
          "CROWDS FILL THE STREETS AS ANGER OVER PRICES "
          "AND RENTS BOILS OVER.",
          art_lisbon, 80)
    panel(cv, 684, 652, 320, 232, GOLD, "SOUTH SUDAN",
          "24 CIVILIANS KILLED IN FRESH VIOLENCE",
          "FIGHTING FLARES AGAIN AS THE UN WARNS OF A "
          "DEEPENING CRISIS.",
          art_sudan, 80)

    # ---- ticker: the rest of the day --------------------------------
    tx, ty, tw, th = 20, 896, 984, 64
    cv.rect(tx, ty, tw, th, INK)
    cv.text("ALSO TODAY", tx + 12, ty + 10, 1, GOLD)
    ticker1 = ("NEPAL PM IN DELHI FOR TALKS WITH MODI  .  SOUTH KOREA "
               "MINISTER QUITS OVER AI EXAM CHEATING")
    ticker2 = ("UN TO KEEP TALKING ON LETHAL AI WEAPONS  .  KIM: NORTH "
               "KOREA SEEKS SECURITY, NOT SUPREMACY")
    cv.text(ticker1, tx + 12, ty + 26, 1, WHITE)
    cv.text(ticker2, tx + 12, ty + 42, 1, WHITE)

    # ---- footer ------------------------------------------------------
    cv.text_center("SOURCES: REUTERS  .  CNN  .  AFP  .  AP", 512, 972, 1,
                   INK_SOFT)
    cv.text_center("DRAWN BY AN AI NEWS ARTIST - NO PHOTOGRAPHS USED",
                   512, 988, 1, GREY)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    data = encode_png(draw_page())
    with open(path, "wb") as f:
        f.write(data)
    print(f"wrote {path} ({len(data)} bytes)")


if __name__ == "__main__":
    main()
