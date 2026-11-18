"""Short: why your SSD drops from 5 GB/s to 800 MB/s (the SLC cache).

Facts (see claude/ssd-slc-cache-short.md in the CC project):
- TechPowerUp, WD Black SN7100 2 TB review, write-intensive test (empty drive, 1 MB sequential,
  single thread): ~5 GB/s until a ~648 GB SLC cache fills, then ~800 MB/s.
- TLC = 3 bits per cell (8 voltage levels); SLC mode = 1 bit (2 levels), so a dynamic cache
  is at most about 1/3 of the flash, and its size depends on how full the drive is (Igor's Lab).
- SATA III SSDs top out around 550 MB/s (6 Gb/s interface).
Build: python -m studio.make videos/2026-11-18-ssd-slc-cache
"""
import math

from studio import *

VIDEO = Video("ssd-slc-cache", format="short",
              question="How full is your game drive right now?")


def gauge_number(f, value, y, color, size=200):
    number(f.c, value, f.cx, y, fmt="{:,.0f}", size=size, color=color)
    text(f.c, "MB/s", f.cx, y + size * 0.72, size=58, color=GREY, weight="bold")


# ------------------------------------------------------------------ 1. hook
@VIDEO.scene("hook", lines=[
    Line("Your SSD says five gigabytes a second.",
         show="Your SSD says 5 GB a second."),
    Line("Copy enough, and it drops to eight hundred. Six times slower.",
         show="Copy enough, and it drops to 800. 6× slower."),
], pad_in=0.1, sfx=[("whoosh", 0.0), ("pop", "five"), ("riser", ("copy", -0.2)), ("hit", "eight"),
                     ("ding", "six")])
def hook(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    # the drive
    d = f.p(0.0, 0.5, "overshoot")
    with moved(c, scale=max(d, 0.001), about=(f.cx, f.top + 170)):
        box(c, f.cx, f.top + 170, 760, 170, fill="#1A2029", stroke=BLUE, width=5, radius=16)
        for i in range(4):
            rect(c, f.cx - 300 + i * 130, f.top + 125, 100, 90, fill=DIM, radius=8)
        rect(c, f.cx + 230, f.top + 135, 90, 70, fill=BLUE, radius=6, alpha=0.8)
        text(c, "NVMe SSD", f.cx, f.top + 300, size=44, color=GREY, weight="bold")
    # the number: rises to 5000, then crashes to 800
    up = f.p("five", 0.9, "out")
    down = f.p("eight", 0.5, "in")
    if up > 0:
        v = lerp(0, 5000, up)
        v = lerp(v, 800, down)
        col = lerp_color(GOLD, RED, down)
        shake = 10 * math.sin(f.t * 60) * max(0, 1 - f.since("eight") * 3) if f.after("eight") else 0
        with moved(c, dx=shake):
            gauge_number(f, v, f.cy - 20, col, size=230)
    # speed meter
    if up > 0:
        k = lerp(up, 0.16, down)
        rect(c, 140, f.cy + 230, 800, 34, fill=DIM, radius=17)
        rect(c, 140, f.cy + 230, 800 * k, 34, fill=lerp_color(GOLD, RED, down), radius=17)
    s = f.p("six", 0.5, "overshoot")
    if s > 0:
        with moved(c, scale=max(s, 0.001), about=(f.cx, f.bottom - 140)):
            runs(c, [("6× ", RED), ("slower", WHITE)], f.cx, f.bottom - 140, size=110, weight="extrabold")


# ------------------------------------------------------------------ 2. the cliff
@VIDEO.scene("cliff", lines=[
    Line("In one review, a two terabyte drive held five gigabytes a second "
         "for six hundred forty-eight gigabytes.",
         show="In one review, a 2 TB drive held 5 GB a second for 648 gigabytes."),
    Line("Then it fell off a cliff."),
], sfx=[("whoosh", 0.0), ("tick", "six"), ("hit", "cliff")])
def cliff(f):
    c = f.c
    x0, x1 = 150, 980
    y0, y1 = f.top + 840, f.top + 280          # y0 = 0 MB/s, y1 = 5000 MB/s
    text(c, "Write speed, WD Black SN7100 2 TB", f.cx, f.top + 70, size=44, color=WHITE, weight="bold")
    text(c, "TechPowerUp test, empty drive", f.cx, f.top + 130, size=34, color=GREY, weight="medium")
    ax = f.p(0.0, 0.6)
    line(c, x0, y0, x1, y0, color=GREY, width=4, progress=ax)
    line(c, x0, y0, x0, y1 - 40, color=GREY, width=4, progress=ax)
    for v, lab in ((5000, "5,000"), (800, "800")):
        yy = lerp(y0, y1, v / 5000)
        text(c, lab, x0 - 14, yy, size=30, color=GREY, align="right", alpha=ax)
        line(c, x0, yy, x1, yy, color=DIM, width=2, alpha=ax)
    text(c, "MB/s", x0 - 14, y1 - 50, size=30, color=GREY, align="right", alpha=ax)
    for g in (0, 648, 2000):
        xx = lerp(x0, x1, g / 2000)
        text(c, f"{g:,}", xx, y0 + 40, size=30, color=GREY, alpha=ax)
    text(c, "GB written", f.cx, y0 + 95, size=32, color=GREY, alpha=ax)

    xc = lerp(x0, x1, 648 / 2000)
    yh, yl = y1, lerp(y0, y1, 800 / 5000)
    # fast part draws as the first line is spoken
    p1 = f.p(("held", 0.0), max(0.8, f.line_end(0) - f.cue("held") - 0.2), "linear")
    stroke_path(c, polyline([(x0, yh), (xc, yh)]), color=GOLD, width=10, progress=p1)
    if p1 > 0:
        text(c, "SLC cache", (x0 + xc) / 2, yh + 50, size=34, color=GOLD, weight="bold", alpha=p1)
    p2 = f.p("cliff", 1.0, "out")
    if p2 > 0:
        stroke_path(c, polyline([(xc, yh), (xc + 8, yl), (x1, yl)]), color=RED, width=10, progress=p2)
        text(c, "cache full", xc + 30, (yh + yl) / 2, size=34, color=RED, weight="bold", align="left",
             alpha=p2)
    b = f.p("six", 0.6)
    if b > 0:
        brace(c, x0, xc, y0 + 150, label="648 GB", color=GOLD, size=44, progress=b)


# ------------------------------------------------------------------ 3. why: voltage levels
def cell(c, cx, top, h, levels, marker, color, alpha=1.0, label=None):
    w = 230
    rect(c, cx - w / 2, top, w, h, stroke=GREY, width=4, radius=14, alpha=alpha)
    for i in range(levels):
        yy = top + h - (i + 0.5) * h / levels
        line(c, cx - w / 2 + 14, yy, cx + w / 2 - 14, yy, color=DIM, width=3, alpha=alpha)
    if marker is not None:
        yy = top + h - marker * h
        rect(c, cx - w / 2 + 10, yy, w - 20, top + h - yy, fill=color, radius=10, alpha=0.35 * alpha)
        line(c, cx - w / 2 + 10, yy, cx + w / 2 - 10, yy, color=color, width=8, alpha=alpha)
    if label:
        text(c, label, cx, top + h + 60, size=46, color=color, weight="bold", alpha=alpha)


@VIDEO.scene("levels", lines=[
    Line("Each flash cell stores three bits as one of eight voltage levels, "
         "which is slow to hit.",
         show="Each flash cell stores 3 bits as one of 8 voltage levels, which is slow to hit."),
    Line("So the drive cheats: one bit per cell, two levels, much faster.",
         show="So the drive cheats: 1 bit per cell, 2 levels, much faster."),
    Line("That's the S L C cache.", show="That's the SLC cache."),
], sfx=[("pop", "cell"), ("tick", "eight"), ("whoosh", "cheats"), ("ding", ("S L C", 0.1))])
def levels(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    top, h = f.top + 260, 640
    # TLC cell on the left: creeps up to level 6 of 8 in tiny steps
    a = f.p("cell", 0.5)
    target = (5 + 0.5) / 8
    if f.after("eight"):
        s = f.since("eight")
        steps = min(int(s / 0.28), 14)
        m = target * (1 - 0.82 ** (steps + 1))
    else:
        m = None
    tx = f.cx - 220 if f.after("cheats") else f.cx
    tx = lerp(f.cx, f.cx - 220, f.p("cheats", 0.6))
    cell(c, tx, top, h, 8, m, BLUE, alpha=a, label="TLC: 3 bits")
    if a > 0:
        text(c, "8 levels", tx, top - 50, size=40, color=GREY, alpha=a)
    sl = f.p("slow", 0.5)
    if sl > 0 and not f.after("cheats"):
        text(c, "slow, careful pulses", tx, top + h + 130, size=40, color=RED, weight="bold", alpha=sl)
    # SLC cell on the right: two levels, one quick jump
    b = f.p("cheats", 0.6)
    if b > 0:
        sx = f.cx + 220
        mm = None
        if f.after("two"):
            mm = 0.75 * f.p("two", 0.25, "out")
        cell(c, sx, top, h, 2, mm, GOLD, alpha=b, label="SLC: 1 bit")
        text(c, "2 levels", sx, top - 50, size=40, color=GREY, alpha=b)
    q = f.p("S L C", 0.5, "overshoot")
    if q > 0:
        with moved(c, scale=max(q, 0.001), about=(f.cx, f.top + 80)):
            text(c, "SLC cache", f.cx, f.top + 80, size=96, color=GOLD, weight="extrabold", glow=10)


# ------------------------------------------------------------------ 4. a third, and free space
@VIDEO.scene("third", lines=[
    Line("One bit instead of three uses three times the space, "
         "so two terabytes gives about six hundred fifty gigabytes of cache.",
         show="1 bit instead of 3 uses 3× the space, so 2 TB gives about 650 GB of cache."),
    Line("It's built from free space, so a full drive gets a tiny cache."),
], sfx=[("pop", "three"), ("tick", "six"), ("whoosh", "free"), ("hit", "tiny")])
def third(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    x0, w = 120, 840
    by = f.top + 330
    text(c, "2 TB of flash", f.cx, by - 90, size=50, color=WHITE, weight="bold", alpha=f.p(0.0, 0.5))
    # used fraction grows during line 2
    used = 0.9 * f.p(f.cue("so", 2) - 0.2, 1.6)
    free = 1 - used
    # 30 cells: grey = your files, gold = cache (3 cells hold what 1 cell of TLC would)
    n = 30
    cols = 10
    size, gap = 72, 12
    k = f.p("three", 0.8)
    for i in range(n):
        r, cc = divmod(i, cols)
        x = x0 + cc * (size + gap)
        y = by + r * (size + gap)
        frac = (i + 0.5) / n
        if frac < used:
            col = GREY
        else:
            col = GOLD if k > 0 and frac < used + free * k else DIM
        rect(c, x, y, size, size, fill=col, radius=8, alpha=f.p(0.0, 0.5))
    # legend
    ly = by + 3 * (size + gap) + 70
    if used > 0.02:
        rect(c, x0, ly - 22, 44, 44, fill=GREY, radius=6)
        text(c, "your files", x0 + 64, ly, size=40, color=GREY, align="left")
    if k > 0:
        rect(c, x0 + 420, ly - 22, 44, 44, fill=GOLD, radius=6, alpha=k)
        text(c, "SLC cache", x0 + 484, ly, size=40, color=GOLD, align="left", alpha=k)
    # the cache size: free space / 3
    cache_gb = 648 * free          # TechPowerUp measured 648 GB empty (~2 TB / 3)
    if f.after("six"):
        number(c, cache_gb, f.cx, f.bottom - 260, fmt="≈ {:,.0f} GB", size=120,
               color=GOLD if used < 0.5 else RED)
        text(c, "fast cache  =  free space ÷ 3", f.cx, f.bottom - 140, size=44, color=WHITE, weight="bold")


# ------------------------------------------------------------------ 5. verdict
@VIDEO.scene("verdict", lines=[
    Line("Slowed down, it still beats a SATA SSD."),
    Line("When idle, it moves that data into three bit cells, and the fast lane comes back.",
         show="When idle, it moves that data into 3-bit cells, and the fast lane comes back."),
], sfx=[("pop", "beats"), ("whoosh", "idle"), ("ding", "back")])
def verdict(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    base = f.top + 720
    scale = 520 / 5000
    items = [("in cache", 5000, "~5,000", GOLD, 0.0),
             ("cache full", 800, "~800", RED, 0.25),
             ("SATA", 550, "~550", GREY, "SATA")]
    xs = [f.cx - 300, f.cx, f.cx + 300]
    for (lab, v, val, col, at), x in zip(items, xs):
        g = f.p(at, 0.7, "out")
        bar(c, x, base, 170, v * scale, color=col, progress=g, label=lab, value=val,
            label_size=40, value_size=50)
    text(c, "MB/s, sequential write", f.cx, base + 110, size=34, color=GREY)
    # idle: the cache refills (gold bar fills back from the right)
    r = f.p("idle", 2.2)
    if r > 0:
        y = f.bottom - 130
        text(c, "idle → data folded into TLC", f.cx, y - 80, size=42, color=BLUE, weight="bold", alpha=min(1, r * 3))
        rect(c, 140, y, 800, 44, fill=DIM, radius=22)
        rect(c, 140, y, 800 * (0.06 + 0.94 * f.p("back", 0.7, "out") if f.after("back") else 0.06 + 0.4 * r),
             44, fill=GOLD, radius=22)
        text(c, "SLC cache", f.cx, y + 100, size=36, color=GOLD, alpha=min(1, r * 3))
