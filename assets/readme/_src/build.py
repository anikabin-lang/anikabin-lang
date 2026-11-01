#!/usr/bin/env python3
"""
Pixel-art asset generator for the Anika Jain GitHub profile README.

Everything is drawn from scratch: a hand-made 5x7 bitmap font, hand-drawn
sprite grids and a few procedural shapes. Output is plain SVG made of
<path> runs (no fonts, no scripts, no external references), so it renders
identically inside GitHub's <img> sandbox.

Run:  python3 assets/readme/_src/build.py
"""
import html
import math
import os

OUT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))

# ── palette ────────────────────────────────────────────────────────────────
BLACK = "#080812"
PINK = "#F04DB8"
GREEN = "#00E58B"
PURPLE = "#6657FF"
SKY = "#A7D8F5"
YELLOW = "#FFE66D"
WHITE = "#FFFFFF"
INK = "#1a0f24"          # sprite outline
PINK_DK = "#b8237f"
PINK_LT = "#ffc2e6"
PINK_MID = "#ff8ad0"
GREEN_DK = "#00a466"
PURPLE_DK = "#3f33c4"
TEAL = "#2ee6d6"
BLUE = "#1e90ff"

# ── 5x7 bitmap font ────────────────────────────────────────────────────────
_F = """
A .###. #...# #...# ##### #...# #...# #...#
B ####. #...# #...# ####. #...# #...# ####.
C .###. #...# #.... #.... #.... #...# .###.
D ####. #...# #...# #...# #...# #...# ####.
E ##### #.... #.... ####. #.... #.... #####
F ##### #.... #.... ####. #.... #.... #....
G .###. #...# #.... #.### #...# #...# .####
H #...# #...# #...# ##### #...# #...# #...#
I ##### ..#.. ..#.. ..#.. ..#.. ..#.. #####
J ..### ...#. ...#. ...#. #..#. #..#. .##..
K #...# #..#. #.#.. ##... #.#.. #..#. #...#
L #.... #.... #.... #.... #.... #.... #####
M #...# ##.## #.#.# #.#.# #...# #...# #...#
N #...# ##..# #.#.# #..## #...# #...# #...#
O .###. #...# #...# #...# #...# #...# .###.
P ####. #...# #...# ####. #.... #.... #....
Q .###. #...# #...# #...# #.#.# #..#. .##.#
R ####. #...# #...# ####. #.#.. #..#. #...#
S .#### #.... #.... .###. ....# ....# ####.
T ##### ..#.. ..#.. ..#.. ..#.. ..#.. ..#..
U #...# #...# #...# #...# #...# #...# .###.
V #...# #...# #...# #...# #...# .#.#. ..#..
W #...# #...# #...# #.#.# #.#.# #.#.# .#.#.
X #...# #...# .#.#. ..#.. .#.#. #...# #...#
Y #...# #...# .#.#. ..#.. ..#.. ..#.. ..#..
Z ##### ....# ...#. ..#.. .#... #.... #####
0 .###. #...# #..## #.#.# ##..# #...# .###.
1 ..#.. .##.. ..#.. ..#.. ..#.. ..#.. .###.
2 .###. #...# ....# ...#. ..#.. .#... #####
3 ####. ....# ....# .###. ....# ....# ####.
4 ...#. ..##. .#.#. #..#. ##### ...#. ...#.
5 ##### #.... ####. ....# ....# #...# .###.
6 .###. #.... #.... ####. #...# #...# .###.
7 ##### ....# ...#. ..#.. .#... .#... .#...
8 .###. #...# #...# .###. #...# #...# .###.
9 .###. #...# #...# .#### ....# ....# .###.
: ..... ..#.. ..#.. ..... ..#.. ..#.. .....
. ..... ..... ..... ..... ..... .##.. .##..
- ..... ..... ..... .###. ..... ..... .....
/ ....# ....# ...#. ..#.. .#... #.... #....
! ..#.. ..#.. ..#.. ..#.. ..#.. ..... ..#..
? .###. #...# ....# ...#. ..#.. ..... ..#..
& .##.. #..#. #.#.. .#... #.#.# #..#. .##.#
+ ..... ..#.. ..#.. ##### ..#.. ..#.. .....
× ..... #...# .#.#. ..#.. .#.#. #...# .....
✦ ..#.. ..#.. .###. ##### .###. ..#.. ..#..
' ..#.. ..#.. .#... ..... ..... ..... .....
, ..... ..... ..... ..... ..#.. ..#.. .#...
( ...#. ..#.. .#... .#... .#... ..#.. ...#.
) .#... ..#.. ...#. ...#. ...#. ..#.. .#...
> .#... ..#.. ...#. ....# ...#. ..#.. .#...
< ...#. ..#.. .#... #.... .#... ..#.. ...#.
_ ..... ..... ..... ..... ..... ..... #####
# .#.#. .#.#. ##### .#.#. ##### .#.#. .#.#.
| ..#.. ..#.. ..#.. ..#.. ..#.. ..#.. ..#..
· ..... ..... ..... .##.. .##.. ..... .....
= ..... ..... ##### ..... ##### ..... .....
▶ #.... ##... ###.. ####. ###.. ##... #....
♥ ..... .#.#. ##### ##### .###. ..#.. .....
— ..... ..... ..... ##### ..... ..... .....
"""
FONT = {" ": ["....."] * 7}
for _line in _F.strip().splitlines():
    _ch, *_rows = _line.split()
    FONT[_ch] = _rows


def text_w(s, scale):
    return len(s) * 6 * scale - scale


# ── SVG builder ────────────────────────────────────────────────────────────
def _n(v):
    v = round(v, 2)
    return str(int(v)) if v == int(v) else str(v)


class SVG:
    def __init__(self, w, h, title=""):
        self.w, self.h = w, h
        self.title = title
        self.defs = []
        self.body = []

    # one <path> per colour per call keeps z-order between calls
    def rects(self, color_rects, opacity=None):
        for color, rs in color_rects.items():
            if not rs:
                continue
            d = "".join(
                f"M{_n(x)} {_n(y)}h{_n(w)}v{_n(h)}h{_n(-w)}z" for x, y, w, h in rs
            )
            op = f' opacity="{opacity}"' if opacity is not None else ""
            self.body.append(f'<path fill="{color}"{op} d="{d}"/>')

    def rect(self, x, y, w, h, color, opacity=None):
        self.rects({color: [(x, y, w, h)]}, opacity)

    def raw(self, s):
        self.body.append(s)

    def text(self, s, x, y, scale, color, shadow=None, sh_off=None, anchor="start"):
        s = s.upper()
        if anchor == "middle":
            x -= text_w(s, scale) / 2
        elif anchor == "end":
            x -= text_w(s, scale)
        if shadow:
            o = sh_off if sh_off is not None else scale
            self.rects({shadow: _glyph_rects(s, x + o, y + o, scale)})
        self.rects({color: _glyph_rects(s, x, y, scale)})
        return text_w(s, scale)

    def sprite(self, grid, pal, x, y, scale, flip=False):
        self.rects(_grid_rects(grid, pal, x, y, scale, flip))

    def canvas(self, cv, x, y, scale):
        self.rects(cv.rects(x, y, scale))

    def bg_dots(self, color=BLACK):
        self.defs.append(
            '<pattern id="dots" width="16" height="16" patternUnits="userSpaceOnUse">'
            f'<rect width="16" height="16" fill="{color}"/>'
            '<rect x="2" y="3" width="2" height="2" fill="#1d1d3c"/>'
            '<rect x="10" y="11" width="2" height="2" fill="#151530"/>'
            '<rect x="12" y="2" width="1" height="1" fill="#2a2a52"/>'
            "</pattern>"
        )
        self.body.insert(0, f'<rect width="{self.w}" height="{self.h}" fill="url(#dots)"/>')

    def save(self, name):
        title = f"<title>{html.escape(self.title)}</title>" if self.title else ""
        defs = f"<defs>{''.join(self.defs)}</defs>" if self.defs else ""
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
            f'viewBox="0 0 {self.w} {self.h}" shape-rendering="crispEdges" role="img">'
            f"{title}{defs}{''.join(self.body)}</svg>"
        )
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"  {name:<28} {len(svg) / 1024:6.1f} KB")


def _glyph_rects(s, x, y, scale):
    out = []
    for i, ch in enumerate(s):
        g = FONT.get(ch, FONT["?"])
        gx = x + i * 6 * scale
        for r, row in enumerate(g):
            c = 0
            while c < 5:
                if row[c] == "#":
                    start = c
                    while c < 5 and row[c] == "#":
                        c += 1
                    out.append((gx + start * scale, y + r * scale, (c - start) * scale, scale))
                else:
                    c += 1
    return out


def _grid_rects(grid, pal, x, y, scale, flip=False):
    rows = [r for r in grid.strip("\n").split("\n")]
    rows = [r.strip() for r in rows]
    width = max(len(r) for r in rows)
    out = {}
    for ry, row in enumerate(rows):
        row = row.ljust(width, ".")
        if flip:
            row = row[::-1]
        c = 0
        while c < width:
            k = row[c]
            if k in pal:
                start = c
                while c < width and row[c] == k:
                    c += 1
                out.setdefault(pal[k], []).append(
                    (x + start * scale, y + ry * scale, (c - start) * scale, scale)
                )
            else:
                c += 1
    return out


def grid_size(grid):
    rows = [r.strip() for r in grid.strip("\n").split("\n")]
    return max(len(r) for r in rows), len(rows)


class Canvas:
    """Small pixel canvas for procedural shapes."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.px = {}

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h and c:
            self.px[(int(x), int(y))] = c

    def fill(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, c)

    def disc(self, cx, cy, r, c):
        for yy in range(int(cy - r - 1), int(cy + r + 2)):
            for xx in range(int(cx - r - 1), int(cx + r + 2)):
                if (xx + 0.5 - cx) ** 2 + (yy + 0.5 - cy) ** 2 <= r * r:
                    self.set(xx, yy, c)

    def ring(self, cx, cy, r, c, t=1.0):
        for yy in range(int(cy - r - 1), int(cy + r + 2)):
            for xx in range(int(cx - r - 1), int(cx + r + 2)):
                d = math.hypot(xx + 0.5 - cx, yy + 0.5 - cy)
                if r - t <= d <= r:
                    self.set(xx, yy, c)

    def line(self, x0, y0, x1, y1, c, dotted=0):
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        err, i = dx + dy, 0
        while True:
            if not dotted or (i // dotted) % 2 == 0:
                self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy
            i += 1

    def blit(self, grid, pal, ox, oy):
        rows = [r.strip() for r in grid.strip("\n").split("\n")]
        for y, row in enumerate(rows):
            for x, k in enumerate(row):
                if k in pal:
                    self.set(ox + x, oy + y, pal[k])

    def rects(self, ox, oy, s):
        out = {}
        for y in range(self.h):
            x = 0
            while x < self.w:
                c = self.px.get((x, y))
                if c:
                    start = x
                    while x < self.w and self.px.get((x, y)) == c:
                        x += 1
                    out.setdefault(c, []).append((ox + start * s, oy + y * s, (x - start) * s, s))
                else:
                    x += 1
        return out


# ── sprites ────────────────────────────────────────────────────────────────
# The player: space buns, purple hoodie with a green ">_" prompt logo.
MASCOT = """
.KKK........KKK.
KHhHK......KHhHK
KHHHKKKKKKKKHHHK
.KKHHHHHHHHHHKK.
.KHHhhHHHHHHHHK.
KHHhHHHHHHHHHHHK
KHHSSSSSSSSSSHHK
KHSSSSSSSSSSSSHK
KHSKKSSSSSSKKSHK
KHSKWSSSSSSKWSHK
KHSPSSSSSSSSPSHK
.KSSSSSKKSSSSSK.
..KSSSSSSSSSSK..
...KKKSSSSKKK...
..KUUUUUUUUUUK..
.KUUUUUWWUUUUUK.
KUUKUUUWWUUUKUUK
KUUKUGUUUUUUKUUK
KUUKUUGUUUUUKUUK
KSSKUGUGGGUUKSSK
.KKKUUUUUUUUKKK.
...KNNNKKNNNK...
...KNNNKKNNNK...
...KNNNKKNNNK...
..KWWWGKKGWWWK..
..KKKKK..KKKKK..
"""
MASCOT_PAL = {
    "K": INK, "H": "#3b2230", "h": "#6e3d55", "S": "#f3b893", "P": "#ff8fb8",
    "W": WHITE, "U": PURPLE, "G": GREEN, "N": "#232a5c",
}

# Walking frame (legs apart) for the footer scene.
MASCOT_WALK = MASCOT.rsplit("\n", 6)[0] + """
...KNNNKKNNNK...
..KNNNK..KNNNK..
.KNNNK....KNNNK.
.KWWGK....KGWWK.
.KKKK......KKKK.
"""

CAT = """
.K...K..........
KPK.KPK.........
KOOKOOK.........
KOOOOOOK........
KOKOOKOK......K.
KWWPPWWK.....KOK
.KWWWWK......KOK
.KFFFFKKKKKKKKOK
.KOOOOOOOOOOOOK.
.KOWWOOOoOoOOOK.
.KOWWOOOOoOOOK..
.KOWWOKOOOKOOK..
.KWWKK.KWK.KWK..
..KK....K...K...
"""
CAT_PAL = {"K": INK, "O": "#ff9f43", "o": "#d9712b", "W": "#fff4e0", "P": "#ff8fb8", "F": PINK}

CLOUD = """
...........WWWW...........
.......WWWWWWWWWW...WWW...
....WWWWWWWWPWWWWWWWWWWWW.
..WWWWWWWPPPPWWWWWWPPWWWWW
.WWWWPPPPBBPPPWWWPPPPPPWWW
WWPPPPBBBBBBBPPPPPBBBBPPPW
.UUBBBBBBBBBBBBBBBBBBBBUU.
...UUUUUUUUUUUUUUUUUUUU...
"""
CLOUD_PAL = {"W": WHITE, "P": "#f7a8d8", "B": SKY, "U": "#8f86ff"}

CLOUD_S = """
....WWWW......
..WWWWWWWW.WW.
.WWWPPWWWWWWWW
WWPPBBPPPWPPPW
.UBBBBBBBBBBU.
..UUUUUUUUUU..
"""

STAR = """
..Y..
..Y..
YYYYY
.YYY.
.Y.Y.
"""
TWINKLE = """
.Y.
YWY
.Y.
"""
STAR_PAL = {"Y": YELLOW, "W": WHITE, "K": INK, "O": "#e0a800"}

BIG_STAR = """
.....KK.....
....KYYK....
....KYYK....
KKKKKYYKKKKK
KYYYYYYYYYOK
.KYYYWYYYOK.
..KYYYYYYK..
..KYYYYYYK..
.KYYYKKYYYK.
.KYYK..KYOK.
KYOK....KOK.
KKK......KK.
"""

HEART = """
.KK.KK.
KPPKPPK
KPWPPPK
KPPPPPK
.KPPPK.
..KPK..
...K...
"""
HEART_PAL = {"K": INK, "P": PINK, "W": WHITE}

COIN = """
.KKKK.
KYYYOK
KYWYOK
KYWYOK
KYYYOK
.KKKK.
"""
COIN_PAL = {"K": INK, "Y": YELLOW, "W": WHITE, "O": "#e0a800"}

KEY = """
.KKK.......
KYYYK......
KYKYKKKKKKK
KYYYKYYYYYK
.KKK.KYKYK.
......K.K..
"""

BUG = """
K.....K
.K.K.K.
..KGK..
.KGGGK.
KGgGgGK
.KGGGK.
K.K.K.K
"""
BUG_PAL = {"K": INK, "G": GREEN, "g": "#0a6b45"}

FLOWER = """
.P.
PYP
.P.
.G.
GG.
.G.
"""

CHEST = """
.KKKKKKKKKKKK.
KOOOOOOOOOOOOK
KOoooooooooOOK
KKKKKKYYKKKKKK
KOOOOOKYKOOOOK
KOooooKKKoooOK
KOOOOOOOOOOOOK
KKKKKKKKKKKKKK
"""
CHEST_PAL = {"K": INK, "O": "#c97a3d", "o": "#9b5523", "Y": YELLOW}

TROPHY = """
...KKKKKKKKKK...
KKKYWYYYYYYyYKKK
KYKYWYYYYYYyYKYK
KYKYWYYKKYYyYKYK
KYKYYYYYKYYyYKYK
.KKYYYYYKYYyYKK.
..KYYYYKKKYyYK..
...KYYYYYYyYK...
....KYYYYyYK....
.....KYYyYK.....
......KYyK......
......KYyK......
.....KYYYyK.....
...KKKKKKKKKK...
...KDDDDDDDDK...
...KKKKKKKKKK...
"""
TROPHY_PAL = {"K": INK, "Y": YELLOW, "y": "#e0a800", "W": WHITE, "D": PURPLE}

MEDAL = """
KPPK........KUUK
.KPPK......KUUK.
..KPPK....KUUK..
...KPPK..KUUK...
....KPPKKUUK....
.....KKKKKK.....
....KSSSSSSK....
...KSWSSSSSsK...
..KSWSSKKSSSsK..
..KSSSKYYKSSsK..
..KSSKYYYYKSsK..
..KSSSKYYKSSsK..
..KSSSSKKSSSsK..
...KSSSSSSSsK...
....KssssssK....
.....KKKKKK.....
"""
MEDAL_PAL = {"K": INK, "P": PINK, "U": PURPLE, "S": "#d6dcf5", "s": "#9aa3cc", "W": WHITE, "Y": YELLOW}

BOOK = """
.KKKKKK.KKKKKK.
KWWWWWWKWWWWWWK
KWLLLWWKWLLLLWK
KWWWWWWKWWWWWWK
KWLLLLWKWLLLWWK
KWWWWWWKWWWWWWK
KWLLLWWKWLLLLWK
KWWWWWWKWWWWWWK
KPPPPPPKPPPPPPK
.KKKKKKKKKKKKK.
"""
BOOK_PAL = {"K": INK, "W": "#fff4e0", "L": "#c9b8d9", "P": PINK}


# ── composite helpers ──────────────────────────────────────────────────────
def ground(svg, y, h=28, w=None):
    w = w or svg.w
    svg.rect(0, y, w, h, GREEN_DK)
    svg.rect(0, y, w, 8, GREEN)
    tufts = []
    for x in range(0, w, 16):
        tufts.append((x + 4, y - 4, 4, 4))
        tufts.append((x + 8, y + 8, 4, 4))
    svg.rects({GREEN: tufts[0::2]})
    svg.rects({"#0a7a50": tufts[1::2]})
    bricks = []
    for row in range(1, h // 8):
        off = 0 if row % 2 else 12
        for x in range(-off, w, 24):
            bricks.append((x, y + 8 * row + 6, 20, 2))
    svg.rects({"#0a7a50": bricks})


def marquee(svg, y, phrase, h=48, offset=40):
    svg.rect(0, y, svg.w, h, PURPLE)
    svg.rect(0, y, svg.w, 4, "#8a7dff")
    svg.rect(0, y + h - 4, svg.w, 4, PURPLE_DK)
    scale = 3
    unit = phrase.upper() + "  ✦  "
    uw = len(unit) * 6 * scale
    ty = y + (h - 7 * scale) // 2
    x = -offset
    while x < svg.w:
        svg.text(unit, x, ty, scale, YELLOW, shadow=PURPLE_DK)
        x += uw


def scatter_stars(svg, pts):
    for (x, y, kind) in pts:
        if kind == "s":
            svg.sprite(STAR, STAR_PAL, x, y, 3)
        elif kind == "t":
            svg.sprite(TWINKLE, STAR_PAL, x, y, 3)
        else:
            svg.rect(x, y, 3, 3, YELLOW)


def tree(svg, x, y, s=6):
    cv = Canvas(24, 30)
    blobs = [(12, 8, 7), (6, 12, 6), (18, 12, 6), (9, 16, 6), (16, 17, 6), (12, 5, 5)]
    for (cx, cy, r) in blobs:
        cv.disc(cx, cy, r, "#0d6e5a")
    for (cx, cy, r) in blobs:
        cv.disc(cx - 1, cy - 1, r - 1.5, GREEN_DK)
    for (cx, cy, r) in blobs:
        cv.disc(cx - 2, cy - 2, r - 3.5, GREEN)
    for (px, py) in [(8, 6), (14, 4), (5, 11), (17, 10), (10, 14), (11, 9)]:
        cv.set(px, py, "#9dffd2")
    cv.fill(11, 20, 3, 10, PURPLE)
    cv.fill(11, 20, 1, 10, "#8a7dff")
    cv.fill(8, 28, 9, 2, PURPLE_DK)
    cv.set(10, 21, PURPLE)
    cv.set(9, 20, PURPLE)
    cv.set(14, 22, PURPLE)
    cv.set(15, 21, PURPLE)
    svg.canvas(cv, x, y, s)


def lamp(svg, x, y, s=5):
    cv = Canvas(14, 40)
    cv.fill(2, 4, 2, 36, PURPLE)
    cv.fill(2, 4, 1, 36, "#8a7dff")
    cv.fill(2, 3, 9, 2, PURPLE)
    cv.fill(8, 5, 5, 3, INK)
    cv.fill(9, 6, 3, 1, GREEN)
    cv.fill(0, 38, 6, 2, PURPLE_DK)
    svg.canvas(cv, x, y, s)
    # light cone
    svg.raw(
        f'<polygon points="{x + 9 * s},{y + 8 * s} {x + 13 * s},{y + 8 * s} '
        f'{x + 18 * s},{y + 40 * s} {x + 4 * s},{y + 40 * s}" fill="{GREEN}" opacity="0.08"/>'
    )


def window_frame(svg, x, y, w, h, label=None, light=PINK_LT, edge="#e0218a"):
    """Pink retro desktop window (drawn, used inside illustrations)."""
    svg.rect(x, y, w, h, edge)
    svg.rect(x + 4, y + 4, w - 8, h - 8, light)
    svg.rect(x + 4, y + 4, w - 8, 22, PINK_MID)
    svg.rect(x + 4, y + 26, w - 8, 3, edge)
    for i in range(2):
        svg.rect(x + 12 + i * 16, y + 9, 10, 12, light)
        svg.rect(x + 14 + i * 16, y + 11, 6, 8, PINK_MID)
    for i in range(3):
        bx = x + w - 20 - i * 16
        svg.rect(bx, y + 9, 12, 12, light)
        svg.rect(bx + 3, y + 12, 6, 6, edge)
    # scrollbar
    svg.rect(x + w - 22, y + 29, 18, h - 33, "#ffd9ef")
    svg.rect(x + w - 22, y + 29, 3, h - 33, edge)
    svg.rect(x + w - 18, y + 40, 10, 40, PINK_MID)
    if label:
        lw = text_w(label, 2) + 24
        lx = x + (w - 22 - lw) // 2
        svg.rect(lx, y + 40, lw, 26, "#e0218a")
        svg.rect(lx + 2, y + 42, lw - 4, 22, "#fff3a8")
        svg.text(label, lx + 12, y + 46, 2, "#c2187a")


# ── assets ─────────────────────────────────────────────────────────────────
def build_hero():
    W, H = 1000, 500
    s = SVG(W, H, "Anika Jain — AI/ML Developer × Full-Stack Developer — Press Start")
    s.bg_dots()

    # status bar
    s.text("XP: AI/ML + FULL-STACK", 40, 22, 2, PINK)
    s.sprite(CLOUD_S, CLOUD_PAL, 360, 12, 4)
    s.sprite(CLOUD, CLOUD_PAL, 470, 8, 3)
    s.sprite(HEART, HEART_PAL, 712, 18, 3)
    s.rect(738, 22, 104, 14, INK)
    s.rect(740, 24, 100, 10, "#1d1d3c")
    s.rect(740, 24, 76, 10, GREEN)
    s.rect(740, 24, 76, 3, "#8bffc9")
    s.text("PLAYER 01", 960, 22, 2, PINK, anchor="end")

    # main frame
    s.raw(f'<rect x="92" y="62" width="816" height="326" rx="22" fill="#000" '
          f'stroke="{GREEN}" stroke-width="4" shape-rendering="geometricPrecision"/>')

    # inside labels
    s.text("LEVEL: DEVELOPER", 124, 88, 2, GREEN)
    s.text("STATUS: BUILDING", 876, 88, 2, YELLOW, anchor="end")

    s.text("AI/ML DEVELOPER × FULL-STACK DEVELOPER", W / 2, 130, 3, YELLOW,
           shadow="#7a5e00", anchor="middle")
    s.text("ANIKA JAIN", W / 2, 166, 11, PINK, shadow=GREEN, sh_off=6, anchor="middle")
    s.text("BUILDING INTELLIGENT SYSTEMS.", W / 2, 268, 2, WHITE, anchor="middle")
    s.text("CREATING MEANINGFUL DIGITAL EXPERIENCES.", W / 2, 290, 2, SKY, anchor="middle")

    # START button
    bx, by, bw, bh = 422, 322, 156, 46
    s.rect(bx + 4, by + bh, bw - 8, 6, GREEN_DK)
    s.rect(bx, by + 4, bw, bh - 4, GREEN)
    s.rect(bx + 4, by, bw - 8, bh + 2, GREEN)
    s.rect(bx + 4, by + 4, bw - 8, 4, "#8bffc9")
    s.text("START", W / 2, by + 14, 4, BLACK, anchor="middle")

    # stars & clouds around the frame
    scatter_stars(s, [(28, 120, "s"), (58, 210, "s"), (34, 300, "t"), (940, 120, "s"),
                      (962, 214, "s"), (180, 46, "p"), (640, 50, "p"), (300, 404, "t"),
                      (690, 410, "p"), (880, 46, "t"), (120, 44, "p"), (560, 404, "p")])
    s.sprite(CLOUD, CLOUD_PAL, -30, 246, 4)
    s.sprite(CLOUD_S, CLOUD_PAL, 930, 280, 5)

    # lamp, tree, player, cat
    lamp(s, 30, 228, 5)
    tree(s, 846, 248, 6)
    s.sprite(MASCOT, MASCOT_PAL, 150, 288, 6)
    s.sprite(CAT, CAT_PAL, 758, 382, 4, flip=True)

    ground(s, 438, 28)
    marquee(s, 466, "ABOUT ME  ✦  TECH STACK  ✦  PROJECT MISSIONS  ✦  ACHIEVEMENTS", h=34, offset=60)
    s.save("hero.svg")


def console(s, x, y, u=4):
    """Pink handheld console (clamshell), origin top-left, unit u px."""
    def R(ax, ay, aw, ah, c):
        s.rect(x + ax * u, y + ay * u, aw * u, ah * u, c)

    P, PD, PL = "#ff2fa8", "#c4157f", "#ff7cc8"
    # lid
    R(1, 0, 78, 48, P)
    R(0, 1, 80, 46, P)
    R(1, 1, 78, 1, PL)
    R(3, 3, 74, 42, "#40404f")
    R(3, 3, 74, 1, "#5a5a6e")
    # camera
    R(39, 4, 2, 2, "#22222c")
    # speaker dots
    for (sx, sy) in [(9, 22), (69, 22)]:
        for (dx, dy) in [(0, -2), (-2, 0), (2, 0), (0, 2), (0, 0)]:
            R(sx + dx, sy + dy, 1, 1, "#22222c")
    # screen
    R(16, 8, 48, 35, "#0e3b31")
    R(16, 8, 48, 35, "#0e3b31")
    for i in range(0, 35, 2):
        R(16, 8 + i, 48, 1, "#114437")
    R(16, 8, 48, 1, "#0a2a23")
    # mascot on screen
    s.sprite(MASCOT, MASCOT_PAL, x + 40 * u - 32, y + 10 * u, 4)
    s.sprite(STAR, STAR_PAL, x + 22 * u, y + 15 * u, 3)
    s.sprite(STAR, STAR_PAL, x + 54 * u, y + 30 * u, 3)
    s.sprite(TWINKLE, STAR_PAL, x + 56 * u, y + 12 * u, 2)
    s.text("P1", x + 18 * u, y + 37 * u, 2, GREEN)
    # side tab
    R(80, 26, 1, 4, "#9a9aab")
    # hinge
    R(5, 48, 70, 5, PD)
    R(5, 48, 70, 1, "#8f0e5c")
    # base
    R(1, 53, 78, 50, P)
    R(0, 54, 80, 48, P)
    R(1, 101, 78, 3, "#a10f68")
    R(1, 54, 78, 1, PL)
    # touch screen
    R(21, 57, 38, 30, "#b01070")
    R(22, 58, 36, 28, "#ffb3e1")
    for gx in range(22, 58, 9):
        R(gx, 58, 1, 28, "#ff9bd6")
    for gy in range(58, 86, 7):
        R(22, gy, 36, 1, "#ff9bd6")
    # circle pad
    cv = Canvas(11, 11)
    cv.disc(5.5, 5.5, 5.5, PD)
    cv.disc(5.5, 5.5, 4, PL)
    cv.disc(4.5, 4.5, 2, "#ffb3e1")
    s.canvas(cv, x + 6 * u, y + 57 * u, u)
    # d-pad
    R(9, 72, 9, 3, PD)
    R(12, 69, 3, 9, PD)
    R(10, 73, 7, 1, PL)
    R(13, 70, 1, 7, PL)
    # ABXY
    for (bx, by) in [(66, 64), (66, 72), (62, 68), (70, 68)]:
        cv = Canvas(4, 4)
        cv.disc(2, 2, 2, PD)
        cv.set(1, 1, PL)
        s.canvas(cv, x + bx * u, y + by * u, u)
    # bottom buttons
    for bx in (27, 37, 47):
        R(bx, 92, 6, 2, PD)
    R(66, 92, 4, 2, PD)
    R(68, 82, 2, 2, GREEN)


def build_level01():
    W, H = 1000, 560
    s = SVG(W, H, "Level 01 — Meet the Player: Anika Jain")
    s.bg_dots()

    # left: level title
    s.text("LEVEL", 40, 56, 9, PINK, shadow=PINK_DK, sh_off=4)
    s.text("01", 40, 130, 9, PINK, shadow=PINK_DK, sh_off=4)
    s.text("MEET THE", 44, 214, 3, PINK)
    s.text("PLAYER", 44, 240, 3, PINK)
    s.text("ANIKA", 42, 290, 6, GREEN, shadow=GREEN_DK, sh_off=3)
    s.text("JAIN", 42, 340, 6, GREEN, shadow=GREEN_DK, sh_off=3)
    s.sprite(CLOUD, CLOUD_PAL, -20, 420, 4)
    s.sprite(BIG_STAR, STAR_PAL, 110, 402, 6)
    scatter_stars(s, [(260, 40, "t"), (230, 400, "p"), (300, 150, "p"), (940, 440, "s"),
                      (650, 30, "t"), (968, 470, "t")])
    s.sprite(CLOUD, CLOUD_PAL, 830, 14, 4)

    # console centre
    cx, cy = 335, 52
    console(s, cx, cy, 4)

    # right: hello window
    wx, wy, ww, wh = 690, 96, 286, 330
    # connector console → window
    s.raw(f'<path d="M{cx + 320} {cy + 40} L{wx} {wy + 10}" stroke="{PINK_LT}" stroke-width="3" '
          'stroke-dasharray="3 7" fill="none"/>')
    window_frame(s, wx, wy, ww, wh, "HELLO !!")
    lines = [
        ("PLAYER:", "ANIKA JAIN"),
        ("CLASS:", "AI/ML +"),
        ("", "FULL-STACK"),
        ("GUILD:", "SRM UNIV."),
        ("", "DELHI NCR"),
        ("MISSION:", "PRACTICAL AI"),
        ("", "FOR REAL"),
        ("", "PROBLEMS"),
        ("STATUS:", "BUILDING"),
    ]
    ty = wy + 82
    for lab, val in lines:
        if lab:
            s.text(lab, wx + 18, ty, 2, "#d0157c")
        s.text(val, wx + 116, ty, 2, PURPLE_DK)
        ty += 24
    s.text("LET'S PLAY!", wx + 18, ty + 6, 2, "#d0157c")
    s.sprite(HEART, HEART_PAL, wx + 160, ty + 2, 3)

    # connectors from console to the three windows below
    base_y = cy + 104 * 4
    for (sx, ex) in [(cx + 40, 167), (cx + 160, 500), (cx + 280, 833)]:
        s.raw(f'<path d="M{sx} {base_y} L{ex} {H}" stroke="{PINK_LT}" stroke-width="3" '
              'stroke-dasharray="3 7" fill="none"/>')
    s.save("level-01-player.svg")


def build_banner(level, title, name, decor, phrase):
    W, H = 1000, 200
    s = SVG(W, H, f"Level {level} — {title}")
    s.bg_dots()
    marquee(s, 0, phrase, h=40, offset=20)
    s.text(f"LEVEL {level}", 56, 74, 8, PINK, shadow=PINK_DK, sh_off=4)
    s.text(title, 60, 148, 4, GREEN, shadow=GREEN_DK, sh_off=2)
    scatter_stars(s, [(600, 60, "t"), (560, 150, "p"), (960, 66, "s"), (700, 172, "p"),
                      (920, 170, "t")])
    s.sprite(CLOUD_S, CLOUD_PAL, 640, 76, 4)
    # mascot + item
    s.sprite(MASCOT, MASCOT_PAL, 820, 82, 4)
    decor(s, 740, 128)
    s.rect(700, 186, 300, 14, GREEN_DK)
    s.rect(700, 186, 300, 4, GREEN)
    s.save(name)


def decor_chest(s, x, y):
    s.sprite(CHEST, CHEST_PAL, x - 10, y + 22, 5)
    s.sprite(TWINKLE, STAR_PAL, x + 60, y + 4, 3)


def decor_flag(s, x, y):
    cv = Canvas(14, 20)
    cv.fill(1, 0, 2, 20, "#c9b8d9")
    cv.fill(3, 1, 10, 7, PINK)
    cv.fill(3, 1, 10, 2, PINK_MID)
    cv.fill(6, 3, 3, 3, YELLOW)
    s.canvas(cv, x, y - 46, 5)


def decor_trophy(s, x, y):
    s.sprite(TROPHY, TROPHY_PAL, x - 10, y - 24, 5)


def decor_book(s, x, y):
    s.sprite(BOOK, BOOK_PAL, x - 12, y + 6, 5)


def decor_heart(s, x, y):
    s.sprite(HEART, HEART_PAL, x - 6, y, 6)
    s.sprite(HEART, HEART_PAL, x + 30, y + 20, 4)


def build_divider(name, phrase):
    s = SVG(1000, 40, phrase)
    marquee(s, 0, phrase, h=40, offset=10)
    s.save(name)


def build_bar(name, label, w=480, accent=PINK, right=None):
    """Window title bar: sits on top of a real-text panel in the README."""
    lw = text_w(label, 2)
    need = 70 + lw + 32 + (text_w(right, 2) + 30 if right else 0) + 70
    W = max(w, need)
    H = 44
    s = SVG(W, H, label)
    edge = "#e0218a"
    s.rect(0, 0, W, H, edge)
    s.rect(3, 3, W - 6, H - 6, PINK_LT)
    s.rect(3, H - 9, W - 6, 6, PINK_MID)
    # accent stripe + icons (left)
    s.rect(10, 10, 14, 18, accent)
    s.rect(10, 10, 14, 4, WHITE)
    s.rect(30, 10, 14, 18, "#ffd9ef")
    s.rect(33, 13, 8, 12, PINK_MID)
    # label chip
    lx = 58
    s.rect(lx, 7, lw + 28, 26, edge)
    s.rect(lx + 2, 9, lw + 24, 22, "#fff3a8")
    s.text(label, lx + 14, 13, 2, "#c2187a")
    if right:
        rw = text_w(right, 2)
        s.text(right, W - 70 - rw, 13, 2, PURPLE_DK)
    # controls (right)
    for i in range(3):
        bx = W - 22 - i * 18
        s.rect(bx, 10, 14, 16, "#ffd9ef")
        s.rect(bx, 10, 14, 2, edge)
        s.rect(bx + 4, 15, 6, 6, edge)
    s.save(name)


def build_button(name, label, fill=GREEN, ink=BLACK, shade=GREEN_DK, hi="#8bffc9"):
    lw = text_w(label, 2)
    W, H = lw + 40, 40
    s = SVG(W, H, label)
    s.rect(4, H - 6, W - 8, 6, shade)
    s.rect(0, 4, W, H - 10, fill)
    s.rect(4, 0, W - 8, H - 4, fill)
    s.rect(4, 4, W - 8, 3, hi)
    s.text(label, 20, 13, 2, ink)
    s.save(name)


def tile(s, size, border):
    s.raw(f'<rect x="3" y="3" width="{size - 6}" height="{size - 6}" rx="14" fill="{BLACK}" '
          f'stroke="{border}" stroke-width="6" shape-rendering="geometricPrecision"/>')


def build_jaldrishti():
    S = 6
    s = SVG(32 * S, 32 * S, "Jaldrishti — stepwell")
    tile(s, 32 * S, TEAL)
    cv = Canvas(32, 32)
    # water glow sky
    for i, c in enumerate(["#0b1f3a", "#0d2747"]):
        cv.fill(3, 3 + i * 3, 26, 3, c)
    # chhatris (pavilions) on the rim
    for ox in (4, 22):
        cv.fill(ox + 1, 4, 4, 1, "#f3c98b")
        cv.fill(ox, 5, 6, 1, "#e0a96d")
        cv.fill(ox, 6, 1, 3, "#c47f45")
        cv.fill(ox + 5, 6, 1, 3, "#c47f45")
        cv.set(ox + 2, 3, "#f3c98b")
        cv.set(ox + 3, 3, "#f3c98b")
    # tiered steps converging down
    tones = ["#f3c98b", "#e0a96d", "#c47f45"]
    y = 9
    for i in range(6):
        x0, x1 = 3 + 2 * i, 28 - 2 * i
        cv.fill(x0, y, x1 - x0 + 1, 1, tones[0])
        cv.fill(x0, y + 1, x1 - x0 + 1, 1, tones[1])
        cv.fill(x0, y + 2, x1 - x0 + 1, 1, tones[2] if i % 2 else tones[1])
        # tiny arches on alternate tiers
        if i in (0, 2):
            for ax in range(x0 + 2, x1 - 1, 4):
                cv.set(ax, y + 1, "#7a4a24")
                cv.set(ax, y + 2, "#7a4a24")
        y += 3
    # water pool
    cv.fill(15, 27, 2, 2, BLUE)
    cv.fill(14, 26, 4, 1, TEAL)
    cv.fill(12, y - 1, 8, 1, TEAL)
    for xx in range(12, 20):
        cv.set(xx, y - 1, TEAL if xx % 3 else WHITE)
    # AI scan brackets
    for (bx, by, dx, dy) in [(5, 10, 1, 1), (26, 10, -1, 1), (5, 28, 1, -1), (26, 28, -1, -1)]:
        cv.set(bx, by, GREEN)
        cv.set(bx + dx, by, GREEN)
        cv.set(bx, by + dy, GREEN)
    s.canvas(cv, 0, 0, S)
    s.save("mission-jaldrishti.svg")


def build_drishti():
    S = 6
    s = SVG(32 * S, 32 * S, "DRISHTI — threat radar")
    tile(s, 32 * S, GREEN)
    cv = Canvas(32, 32)
    c = (16, 16)
    cv.disc(*c, 12.5, "#06281b")
    # sweep wedge
    for yy in range(32):
        for xx in range(32):
            dx, dy = xx + 0.5 - 16, yy + 0.5 - 16
            d = math.hypot(dx, dy)
            a = math.degrees(math.atan2(-dy, dx)) % 360
            if d <= 12 and 20 <= a <= 70:
                cv.set(xx, yy, "#0a6b45" if a < 62 else "#13a86b")
    for r in (12.5, 8.5, 4.5):
        cv.ring(*c, r, "#0f8a58")
    cv.line(4, 16, 27, 16, "#0f8a58")
    cv.line(16, 4, 16, 27, "#0f8a58")
    cv.line(16, 16, 24, 8, GREEN)
    # network nodes + links
    nodes = [(10, 10), (22, 21), (11, 22), (20, 12)]
    for (a, b) in [(0, 2), (2, 1), (1, 3), (0, 3)]:
        cv.line(*nodes[a], *nodes[b], SKY, dotted=1)
    for (nx, ny) in nodes:
        cv.fill(nx - 1, ny - 1, 2, 2, SKY)
    # threats
    cv.fill(21, 20, 3, 3, "#ff3b6b")
    cv.set(22, 21, WHITE)
    cv.fill(19, 11, 2, 2, "#ff3b6b")
    # alert badge
    cv.fill(24, 3, 5, 7, YELLOW)
    cv.fill(26, 4, 1, 3, INK)
    cv.set(26, 8, INK)
    s.canvas(cv, 0, 0, S)
    s.save("mission-drishti.svg")


def build_back2u():
    S = 6
    s = SVG(32 * S, 32 * S, "BACK2U — lost & found search")
    tile(s, 32 * S, YELLOW)
    cv = Canvas(32, 32)
    # campus ground
    cv.fill(3, 25, 26, 4, "#0d6e5a")
    cv.fill(3, 25, 26, 1, GREEN)
    # backpack (the found item)
    bp = """
    ..KKKK..
    .KK..KK.
    KKKKKKKK
    KPPPPPPK
    KPpPPpPK
    KKKKKKKK
    KPKYYKPK
    KPKKKKPK
    KPPPPPPK
    KPPPPPPK
    .KKKKKK.
    """
    cv.blit(bp, {"K": INK, "P": PINK, "p": PINK_LT, "Y": YELLOW}, 6, 14)
    # dotted match box
    for i in range(4, 17, 2):
        cv.set(i, 12, GREEN)
        cv.set(i, 26, GREEN)
    for j in range(12, 27, 2):
        cv.set(4, j, GREEN)
        cv.set(16, j, GREEN)
    # check mark
    for (px, py) in [(4, 8), (5, 9), (6, 10), (7, 9), (8, 8), (9, 7), (10, 6)]:
        cv.set(px, py, GREEN)
    # magnifying glass
    cv.disc(21, 12, 6.5, INK)
    cv.disc(21, 12, 5, "#2b5d7d")
    cv.disc(20, 11, 3, "#3f86b0")
    cv.set(18, 9, WHITE)
    cv.set(19, 9, WHITE)
    cv.set(18, 10, WHITE)
    for k in range(6):
        cv.fill(25 + k, 16 + k, 2, 2, PURPLE)
    cv.fill(25, 16, 1, 1, INK)
    # sparkle
    cv.set(27, 4, YELLOW)
    cv.set(26, 5, YELLOW)
    cv.set(28, 5, YELLOW)
    cv.set(27, 6, YELLOW)
    cv.set(27, 5, WHITE)
    s.canvas(cv, 0, 0, S)
    s.save("mission-back2u.svg")


def build_achievement_icon(name, grid, pal, border, label):
    S = 128
    s = SVG(S, S, label)
    tile(s, S, border)
    s.sprite(grid, pal, 16, 14, 6)
    s.sprite(TWINKLE, STAR_PAL, 14, 14, 3)
    s.sprite(TWINKLE, STAR_PAL, 100, 90, 3)
    s.save(name)


def build_footer():
    W, H = 1000, 330
    s = SVG(W, H, "Next level — exit portal")
    s.bg_dots()
    s.sprite(CLOUD, CLOUD_PAL, -24, 40, 4)
    s.sprite(CLOUD_S, CLOUD_PAL, 880, 30, 5)
    s.sprite(CLOUD_S, CLOUD_PAL, 470, 22, 3)
    scatter_stars(s, [(200, 30, "s"), (330, 80, "t"), (620, 40, "s"), (760, 90, "p"),
                      (90, 140, "p"), (960, 150, "t"), (420, 120, "p")])
    s.text("CONTINUE?", 300, 120, 4, YELLOW, shadow="#7a5e00", sh_off=2)
    s.text("▶ YES", 540, 120, 4, GREEN, shadow=GREEN_DK, sh_off=2)

    gy = 258
    # coins, key, bugs
    for cx in (100, 160, 220, 720, 770):
        s.sprite(COIN, COIN_PAL, cx, 196, 6)
    s.sprite(KEY, COIN_PAL, 420, 176, 6)
    s.sprite(BUG, BUG_PAL, 330, 150, 5)
    s.sprite(BUG, BUG_PAL, 560, 166, 5)
    # flowers
    for fx, col in [(60, PINK), (140, YELLOW), (280, PINK), (380, SKY), (520, YELLOW),
                    (720, PINK), (790, SKY), (960, YELLOW)]:
        s.sprite(FLOWER, {"P": col, "Y": WHITE if col != YELLOW else PINK, "G": GREEN},
                 fx, gy - 24, 4)
    s.sprite(CHEST, CHEST_PAL, 200, gy - 32, 4)
    # player heading to the exit, cat following
    s.sprite(MASCOT_WALK, MASCOT_PAL, 640, gy - 104, 4)
    s.sprite(CAT, CAT_PAL, 520, gy - 56, 4, flip=True)
    # flag
    cv = Canvas(10, 22)
    cv.fill(0, 0, 1, 22, "#c9b8d9")
    cv.fill(1, 1, 7, 5, "#ff3b6b")
    cv.fill(1, 1, 7, 1, "#ff8fa8")
    s.canvas(cv, 800, gy - 88, 4)
    # exit portal: stone arch with glowing core
    px, py = 860, gy - 128
    cv = Canvas(26, 32)
    for yy in range(32):
        for xx in range(26):
            inside_outer = (yy >= 10 and 0 <= xx < 26) or math.hypot(xx + 0.5 - 13, yy + 0.5 - 11) <= 13
            if inside_outer:
                cv.set(xx, yy, "#8b8fa8" if (xx // 4 + yy // 3) % 2 else "#a9adc4")
    for yy in range(32):
        for xx in range(26):
            inner = (yy >= 11 and 4 <= xx < 22) or math.hypot(xx + 0.5 - 13, yy + 0.5 - 12) <= 9
            if inner:
                d = math.hypot(xx + 0.5 - 13, yy + 0.5 - 20)
                cv.set(xx, yy, WHITE if d < 3 else "#ff8ad0" if d < 6 else PINK if d < 9 else PURPLE)
    for (sx, sy) in [(8, 14), (17, 17), (10, 25), (15, 9)]:
        cv.set(sx, sy, YELLOW)
    s.canvas(cv, px, py, 5)
    s.text("EXIT", px + 65, py - 28, 3, GREEN, anchor="middle")

    ground(s, gy, 32)
    marquee(s, gy + 32, "THANKS FOR PLAYING  ✦  SEE YOU IN THE NEXT LEVEL", h=40, offset=30)
    s.save("footer-world.svg")


def main():
    os.makedirs(OUT, exist_ok=True)
    print("building assets →", OUT)
    build_hero()
    build_level01()
    build_banner("02", "PLAYER LOADOUT", "level-02-loadout.svg", decor_chest,
                 "TECH STACK  ✦  PLAYER LOADOUT")
    build_banner("03", "MISSIONS UNLOCKED", "level-03-missions.svg", decor_flag,
                 "PROJECT MISSIONS  ✦  FEATURED BUILDS")
    build_banner("04", "ACHIEVEMENTS", "level-04-achievements.svg", decor_trophy,
                 "ACHIEVEMENTS UNLOCKED  ✦  HIGH SCORES")
    build_banner("05", "PLAYER STATISTICS", "level-05-stats.svg", decor_heart,
                 "PLAYER STATUS  ✦  GITHUB ACTIVITY")
    build_divider("divider-log.svg", "PLAYER LOG  ✦  CERTIFICATIONS & LEARNING")
    build_divider("divider-next.svg", "NEXT LEVEL  ✦  CONTACT")

    # window title bars
    build_bar("bar-profile.svg", "PLAYER PROFILE", 340)
    build_bar("bar-training.svg", "TRAINING LOG", 340, accent=GREEN)
    build_bar("bar-interests.svg", "CURRENT INTERESTS", 340, accent=YELLOW)
    build_bar("bar-languages.svg", "PROGRAMMING LANGUAGES", 480)
    build_bar("bar-aiml.svg", "AI / ML & DATA SCIENCE", 480, accent=GREEN)
    build_bar("bar-fullstack.svg", "FULL-STACK DEVELOPMENT", 480, accent=PURPLE)
    build_bar("bar-databases.svg", "DATABASES", 480, accent=SKY)
    build_bar("bar-core.svg", "CORE COMPUTER SCIENCE", 480, accent=YELLOW)
    build_bar("bar-tools.svg", "TOOLS & PLATFORMS", 480, accent=GREEN)
    build_bar("bar-mission-01.svg", "MISSION 01 ▶ JALDRISHTI", 980, accent=TEAL, right="2026 — PRESENT")
    build_bar("bar-mission-02.svg", "MISSION 02 ▶ DRISHTI", 980, accent=GREEN, right="2026 — PRESENT")
    build_bar("bar-mission-03.svg", "MISSION 03 ▶ BACK2U", 980, accent=YELLOW, right="2026 — PRESENT")
    build_bar("bar-achievement-01.svg", "ACHIEVEMENT 01 ✦ 1ST PLACE", 480, accent=YELLOW)
    build_bar("bar-achievement-02.svg", "ACHIEVEMENT 02 ✦ FINALIST", 480, accent=PURPLE)
    build_bar("bar-log.svg", "PLAYER LOG", 980, accent=GREEN, right="QUESTS COMPLETED")
    build_bar("bar-stats.svg", "PLAYER STATUS", 980, accent=PINK, right="LIVE FROM GITHUB")

    # buttons
    build_button("btn-start.svg", "▶ PRESS START")
    build_button("btn-repo.svg", "▶ VIEW REPO")
    build_button("btn-demo.svg", "▶ PLAY DEMO", fill=YELLOW, shade="#c9a800", hi="#fff6b8")
    build_button("btn-certificate.svg", "✦ CERTIFICATE", fill=SKY, shade="#5fa6cf", hi="#e3f4ff")
    build_button("btn-github.svg", "GITHUB", fill=PINK, ink=WHITE, shade=PINK_DK, hi="#ff9fd8")
    build_button("btn-linkedin.svg", "LINKEDIN", fill=PURPLE, ink=WHITE, shade=PURPLE_DK, hi="#a49bff")
    build_button("btn-portfolio.svg", "PORTFOLIO", fill=GREEN, shade=GREEN_DK)

    # illustrations
    build_jaldrishti()
    build_drishti()
    build_back2u()
    build_achievement_icon("achievement-trophy.svg", TROPHY, TROPHY_PAL, YELLOW, "Winner trophy")
    build_achievement_icon("achievement-medal.svg", MEDAL, MEDAL_PAL, PURPLE, "Finalist medal")
    build_footer()


if __name__ == "__main__":
    main()
