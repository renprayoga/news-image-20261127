# main.py — "One Day on Earth": Friday 27 November 2026 in one image.
#
# A deterministic newspaper front page drawn with the stdlib-only raster
# engine in render.py. No network, no files read, no clock, no randomness:
# two runs write byte-identical PNGs.
#
# News research (checked 27 Nov 2026, ~07:40 WIB, from Reuters / BBC /
# NYT / AP wires as carried that morning):
#   Lead  — Iranian drone strike kills two Italian workers in Kuwait;
#           Iran denies responsibility (reported ~01:00 UTC, 27 Nov).
#   Gaza  — Hamas weighs its response after Israel kills 10 in Gaza.
#   Odesa — Russia hits two grain ships carrying 100,000+ tonnes.
#   Trade — Black Friday shoppers spend on despite inflation; Tokyo core
#           CPI +2.9%; Trump seeks a probe into "fake" US GDP figures
#           after growth is revised up to 4.3%.
#   Brief — UK migration, Depardieu trial, Ibiza tanker, Musk / SpaceX,
#           Gukesh-Sindarov draw, NZ v India Test, Macy's parade storm,
#           Ebola in Congo, Kim Jong Un, Guinea-Bissau, Serbia, Brazil,
#           India rupee, Argentina primaries, plus Nyrstar, China drones
#           and the NZ election count.

import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from render import Sheet, text_width, wrap, write_png

# ---------------------------------------------------------------- palette

PAPER = (243, 234, 211)
INK = (26, 26, 22)
RED = (178, 34, 28)
NAVY = (22, 41, 77)
NAVY_DARK = (15, 27, 52)
GOLD = (198, 138, 32)
ORANGE = (232, 110, 20)
MUTED = (112, 101, 82)
RULE = (196, 182, 148)
CREAM = (243, 234, 211)
SLATE = (96, 104, 122)
SEA = (36, 68, 104)
DUSK_TOP = (58, 30, 44)
DUSK_MID = (96, 52, 52)
DUSK_LOW = (150, 90, 60)

W, H = 1024, 1024
M = 28                 # page margin
CW = W - 2 * M         # content width: 968


# ---------------------------------------------------------------- data

LEAD = {
    "kicker": "GULF — KUWAIT  •  LEAD STORY",
    "headline": "IRANIAN DRONE STRIKE KILLS TWO ITALIANS IN KUWAIT",
    "body": ("Two Italian technicians working for German defence group "
             "Rheinmetall are killed in a drone attack Kuwait blames on "
             "Iran. Tehran denies any role."),
    "second": ("Kuwait says its air defences tracked the drones "
               "overnight; Rome demands answers as Gulf tensions climb."),
    "dateline": "KUWAIT CITY — REPORTED 01:00 UTC  •  REUTERS / NYT / BBC",
}

CARDS = [
    {
        "kicker": "MIDDLE EAST — GAZA",
        "headline": "HAMAS WEIGHS REPLY AFTER ISRAEL KILLS 10 IN GAZA",
        "body": ("Israel kills 10 people in Gaza and Hamas weighs its "
                 "response, putting the fragile ceasefire under fresh strain."),
        "scene": "gaza",
    },
    {
        "kicker": "BLACK SEA — ODESA",
        "headline": "RUSSIA HITS TWO GRAIN SHIPS OFF ODESA",
        "body": ("Moscow strikes two foreign cargo ships carrying more "
                 "than 100,000 tonnes of grain near Ukraine's Black Sea ports."),
        "scene": "odesa",
    },
]

MARKETS = [
    {
        "title": "BLACK FRIDAY",
        "chart": "bars",
        "caption": ("US SHOPPERS SPEND ON DESPITE INFLATION — HOLIDAY "
                    "SALES SEEN PAST $1 TRILLION"),
    },
    {
        "title": "TOKYO CPI +2.9%",
        "chart": "line",
        "caption": ("CORE INFLATION TOPS THE BANK OF JAPAN'S 2% TARGET "
                    "FOR A THIRD MONTH"),
    },
    {
        "title": "US GDP REVISED UP",
        "chart": "bignum",
        "caption": ("TRUMP SEEKS A PROBE INTO 'FAKE' FIGURES AS GROWTH "
                    "BEATS FORECASTS"),
    },
]

BRIEFS_LEFT = [
    "UK NET MIGRATION LOWEST SINCE 1997",
    "DEPARDIEU TO STAND TRIAL OVER 2018 RAPE CLAIM",
    "TANKER CAPSIZES OFF IBIZA; ONE DEAD, 7,000 T ABOARD",
    "MUSK: EVERY US CHILD TO GET TWO SPACEX SHARES",
    "CHESS: GUKESH, SINDAROV DRAW MARATHON GAME 3",
    "NZ 77-1 AT LUNCH IN 2ND TEST V INDIA",
    "STORM HALTS MACY'S 100TH PARADE; 500,000 HOMES DARK",
]
BRIEFS_RIGHT = [
    "EBOLA IN CONGO PASSES 12,000 CASES",
    "KIM JONG UN VOWS PERMANENT NUCLEAR ARMAMENT",
    "GUINEA-BISSAU DELAYS POLLS TWO YEARS AFTER COUP",
    "SERBIA TO VOTE FOR PRESIDENT ON 27 DECEMBER",
    "BRAZIL INFLATION EASES BELOW FORECASTS",
    "INDIA RUPEE BULLS RETURN AFTER 18 MONTHS",
    "ARGENTINA SENATE SUSPENDS 2027 PRIMARIES",
]
ALSO = ("ALSO: NYRSTAR HALTS DUTCH ZINC OUTPUT  •  CHINA'S DRONES "
        "RESHAPE ASIAN MILITARIES  •  NZ FINAL ELECTION COUNT DUE TODAY")

# Places on the strip, ordered west to east by longitude.
PLACES = ["NEW YORK", "LONDON", "PARIS", "IBIZA", "CONGO", "ODESA",
          "GAZA", "KUWAIT", "PYONGYANG", "TOKYO", "CHRISTCHURCH"]

STORY_COUNT = (1 + len(CARDS) + len(MARKETS) + len(BRIEFS_LEFT)
               + len(BRIEFS_RIGHT) + 3)   # 3 items in the ALSO line


# ---------------------------------------------------------------- helpers

def _lcg(seed):
    """Deterministic pseudo-random stream (fixed seed, no time input)."""
    state = seed & 0x7FFFFFFF
    while True:
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        yield state


def _stars(sheet, x, y, w, h, n, seed):
    rnd = _lcg(seed)
    for _ in range(n):
        sx = x + next(rnd) % w
        sy = y + next(rnd) % h
        sheet.px(sx, sy, (235, 230, 210))
        if next(rnd) % 4 == 0:
            sheet.px(sx + 1, sy, (235, 230, 210))


def _skyline(sheet, x, y_base, w, color, seed, lo, hi):
    rnd = _lcg(seed)
    cx = x
    while cx < x + w:
        bw = 14 + next(rnd) % 26
        bh = lo + next(rnd) % (hi - lo)
        sheet.rect(cx, y_base - bh, bw, bh, color)
        if next(rnd) % 3 == 0:  # antenna
            sheet.rect(cx + bw // 2, y_base - bh - 8, 2, 8, color)
        cx += bw + 3


def _windows(sheet, x, y_base, w, h, seed, color):
    rnd = _lcg(seed)
    for wy in range(y_base - h + 6, y_base - 4, 9):
        for wx in range(x + 4, x + w - 4, 9):
            if next(rnd) % 3 == 0:
                sheet.rect(wx, wy, 3, 4, color)


def _explosion(sheet, cx, cy, r):
    sheet.disc(cx, cy, r, (232, 110, 20))
    sheet.disc(cx, cy - r // 4, int(r * 0.7), (245, 170, 40))
    sheet.disc(cx, cy - r // 3, int(r * 0.4), (250, 225, 120))
    sheet.tri(cx - r, cy + r // 2, cx, cy - int(r * 1.6), cx + r, cy + r // 2,
              (245, 170, 40))


def _smoke(sheet, cx, cy, color=(140, 136, 128)):
    sheet.disc(cx, cy, 8, color)
    sheet.disc(cx + 10, cy - 8, 6, color)
    sheet.disc(cx - 9, cy - 6, 6, color)


# ---------------------------------------------------------------- scenes

def scene_kuwait(sheet, x, y, w, h):
    """Night over the Gulf: refinery skyline, drones, one big blast."""
    sheet.rect(x, y, w, h, NAVY_DARK)
    sheet.rect(x, y, w, h // 3, (20, 36, 68))
    _stars(sheet, x, y, w, h // 2, 90, 27)
    # Distant refinery skyline.
    _skyline(sheet, x + 8, y + h - 62, w - 16, (10, 18, 36), 41, 22, 58)
    # Two flare towers.
    for tx in (x + w - 92, x + w - 52):
        sheet.rect(tx, y + 58, 10, h - 120, (24, 28, 40))
        sheet.tri(tx - 4, y + 58, tx + 5, y + 34, tx + 14, y + 58, ORANGE)
        sheet.disc(tx + 5, y + 40, 4, (250, 225, 120))
    _explosion(sheet, x + 82, y + 84, 21)
    _smoke(sheet, x + 82, y + 52)
    # Three drones with faint trails.
    for dx, dy in ((x + 200, y + 42), (x + 268, y + 66), (x + 330, y + 36)):
        sheet.line(dx - 26, dy + 12, dx, dy, (120, 120, 130))
        sheet.poly([(dx - 9, dy), (dx, dy - 4), (dx + 9, dy), (dx, dy + 4)],
                   (12, 12, 16))
        sheet.disc(dx, dy, 2, RED)
    # Sea + reflection.
    sheet.rect(x, y + h - 62, w, 40, SEA)
    for wy in (y + h - 52, y + h - 42, y + h - 32):
        sheet.hline(x + 12, wy, w - 24, (90, 130, 170))
    sheet.rect(x + 76, y + h - 62, 12, 40, (190, 110, 35))
    # Caption strip.
    sheet.rect(x, y + h - 22, w, 22, (10, 10, 12))
    sheet.text(x + 10, y + h - 16, "DRONES OVER THE GULF — KUWAIT CITY, OVERNIGHT",
               1, CREAM)


def scene_gaza(sheet, x, y, w, h):
    """Dusk skyline in Gaza with a blast column and a low moon."""
    for i, col in enumerate((DUSK_TOP, DUSK_MID, DUSK_LOW)):
        sheet.rect(x, y + i * h // 3, w, h // 3 + 1, col)
    sheet.disc(x + w - 52, y + 24, 13, (240, 200, 110))
    _skyline(sheet, x + 6, y + h, w - 12, (28, 16, 22), 77, 26, 62)
    _windows(sheet, x + 6, y + h, w - 12, 62, 91, (240, 190, 90))
    _explosion(sheet, x + w // 2, y + h - 46, 20)
    _smoke(sheet, x + w // 2, y + h - 92)
    sheet.rect(x, y + h - 3, w, 3, (20, 12, 14))


def scene_odesa(sheet, x, y, w, h):
    """Grey Black Sea morning: two grain ships, one missile streak."""
    sheet.rect(x, y, w, h, (52, 66, 84))
    sheet.rect(x, y, w, h // 2, (70, 84, 102))
    _stars(sheet, x, y, w, h // 3, 24, 113)
    sea_y = y + h // 2
    sheet.rect(x, sea_y, w, h - h // 2, (28, 52, 78))
    for wy in (sea_y + 12, sea_y + 26, sea_y + 40):
        sheet.hline(x + 10, wy, w - 20, (80, 115, 150))
    # Missile streak, top right to the far ship.
    sheet.line(x + w - 30, y + 8, x + w - 150, y + 58, (250, 240, 220))
    sheet.line(x + w - 30, y + 8, x + w - 150, y + 58, (245, 170, 40))
    sheet.disc(x + w - 32, y + 9, 3, (250, 225, 120))
    # Two grain ships.
    for sx, hull in ((x + 26, (16, 20, 30)), (x + w - 210, (16, 20, 30))):
        sheet.rect(sx, sea_y + 18, 150, 20, hull)
        sheet.rect(sx + 8, sea_y + 26, 134, 6, (150, 60, 40))
        sheet.rect(sx + 96, sea_y + 2, 34, 16, (225, 220, 205))
        sheet.rect(sx + 60, sea_y + 8, 26, 10, (225, 220, 205))
        sheet.rect(sx + 30, sea_y - 6, 4, 24, (16, 20, 30))
    _explosion(sheet, x + w - 130, sea_y + 6, 12)
    _smoke(sheet, x + w - 130, sea_y - 26)


# ---------------------------------------------------------------- page

def build():
    s = Sheet(W, H, PAPER)
    s.rect(0, 0, W, 10, RED)

    # ---- masthead
    s.text_centred(W // 2, 20, "ONE DAY ON EARTH", 6, INK)
    s.text_centred(W // 2, 70, "FRIDAY 27 NOVEMBER 2026", 2, RED)
    sub = ("%d STORIES  •  11 PLACES  •  SEVEN REGIONS  —  "
           "THE WORLD IN A SINGLE PAGE" % STORY_COUNT)
    s.text_centred(W // 2, 92, sub, 1, MUTED)
    s.hline(M, 106, CW, INK, 2)
    s.hline(M, 110, CW, INK, 1)

    # ---- lead story: text left, scene right
    ly = 120
    tx, tw = M, 500
    sx, sw, sh = M + 516, 452, 240
    s.text(tx, ly, LEAD["kicker"], 2, RED)
    y = s.para(tx, ly + 26, LEAD["headline"], tw, 3, INK, leading=28)
    y = s.para(tx, y + 8, LEAD["body"], tw, 2, INK, leading=17)
    y = s.para(tx, y + 6, LEAD["second"], tw, 2, MUTED, leading=17)
    s.hline(tx, y + 10, tw, GOLD, 2)
    s.text(tx, y + 18, LEAD["dateline"], 1, MUTED)
    scene_kuwait(s, sx, ly, sw, sh)
    s.frame(sx, ly, sw, sh, INK, 1)

    # ---- two picture cards
    cy = 374
    ch = 226
    for i, card in enumerate(CARDS):
        cx = M + i * (476 + 16)
        s.frame(cx, cy, 476, ch, INK, 1)
        if card["scene"] == "gaza":
            scene_gaza(s, cx + 1, cy + 1, 474, 132)
        else:
            scene_odesa(s, cx + 1, cy + 1, 474, 132)
        ty = cy + 140
        s.text(cx + 10, ty, card["kicker"], 1, RED)
        y = s.para(cx + 10, ty + 13, card["headline"], 456, 2, INK, leading=16)
        s.para(cx + 10, y + 3, card["body"], 456, 1, MUTED, leading=10)

    # ---- where-it-happened strip: one route line, west to east, with a
    # dot per place and alternating labels (a wide, short band cannot
    # hold a geographic bitmap without stretching it into bars).
    my = 614
    s.text(M, my, "WHERE THE DAY HAPPENED — 11 PLACES, ONE FRIDAY", 1, RED)
    s.text(W - M - text_width("WEST TO EAST", 1), my,
           "WEST TO EAST", 1, MUTED)
    line_y = my + 66
    for dx in range(M + 8, M + CW - 8, 16):
        s.hline(dx, line_y, 8, SLATE, 1)
    n = len(PLACES)
    for i, name in enumerate(PLACES):
        cx = int(M + (i + 0.5) * CW / n)
        s.ring(cx, line_y, 5, PAPER, 1)
        s.disc(cx, line_y, 4, RED)
        if i % 2 == 0:
            s.text_centred(cx, line_y - 16, name, 1, INK)
        else:
            s.text_centred(cx, line_y + 12, name, 1, INK)
    region = ("GULF 1  •  MIDDLE EAST 1  •  EUROPE 4  •  ASIA 2  •  "
              "AMERICAS 1  •  OCEANIA 1  •  AFRICA 1")
    s.text_centred(W // 2, line_y + 30, region, 1, MUTED)

    # ---- markets band
    ky = 758
    kh = 108
    s.rect(M, ky, CW, kh, NAVY)
    s.text(M + 16, ky + 10, "TRADE & MARKETS", 2, GOLD)
    s.text(W - M - 16 - text_width("BLACK FRIDAY • 27 NOV", 1), ky + 12,
           "BLACK FRIDAY • 27 NOV", 1, GOLD)
    s.hline(M + 16, ky + 32, CW - 32, GOLD, 1)
    for i, mkt in enumerate(MARKETS):
        col_x = M + 16 + i * 322
        s.text(col_x, ky + 42, mkt["title"], 2, CREAM)
        if mkt["chart"] == "bars":
            base = ky + 100
            for b, bh in enumerate((10, 16, 22, 28, 24)):
                bx = col_x + 150 + b * 16
                s.rect(bx, base - bh, 11, bh, ORANGE if b == 3 else GOLD)
            s.para(col_x, ky + 62, mkt["caption"], 132, 1, (200, 205, 220),
                   leading=10)
        elif mkt["chart"] == "line":
            pts = [(col_x + 150 + k * 14, ky + 100 - k * 5) for k in range(6)]
            for a, b in zip(pts, pts[1:]):
                s.line(a[0], a[1], b[0], b[1], (245, 170, 40))
            s.tri(pts[-1][0], pts[-1][1] - 7, pts[-1][0] - 9, pts[-1][1] + 5,
                  pts[-1][0] + 7, pts[-1][1] + 3, RED)
            s.para(col_x, ky + 62, mkt["caption"], 132, 1, (200, 205, 220),
                   leading=10)
        else:  # bignum
            s.text(col_x + 210, ky + 40, "4.3%", 4, GOLD)
            s.para(col_x, ky + 74, mkt["caption"], 290, 1, (200, 205, 220),
                   leading=10)

    # ---- the day in brief
    by = 880
    s.text(M, by, "THE DAY IN BRIEF", 1, RED)
    s.hline(M, by + 11, CW, INK, 1)
    row_y = by + 18
    for col_i, items in enumerate((BRIEFS_LEFT, BRIEFS_RIGHT)):
        bx = M + col_i * 492
        for j, item in enumerate(items):
            yy = row_y + j * 10
            s.disc(bx + 3, yy + 3, 2, RED)
            s.text(bx + 10, yy, item, 1, INK)

    # ---- also + footer
    ay = row_y + 7 * 10 + 6
    s.text(M, ay, ALSO, 1, MUTED)
    s.hline(M, ay + 12, CW, INK, 1)
    s.text_centred(W // 2, ay + 18, "SOURCES: REUTERS  •  BBC  •  CNN  •  AFP  •  AP",
                   1, MUTED)
    return s


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    sheet = build()
    size = write_png(sheet, path)
    digest = hashlib.sha256(open(path, "rb").read()).hexdigest()
    print("wrote %s (%dx%d, %d bytes, sha256 %s)"
          % (path, W, H, size, digest))


if __name__ == "__main__":
    main()
