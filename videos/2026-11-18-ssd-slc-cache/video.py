"""Short (v2, simpler): why your SSD drops from 5,000 to 800 MB/s.

v2 (Nov 18, 2026): the creator found v1 hard to follow. One metaphor carries the whole video:
a flash cell is a glass of water. 3 bits = fill to one of 8 exact lines (slow, careful pour);
1 bit = just empty or full (fast). The fast "one-bit" glasses are the SLC cache.

Facts (see claude/ssd-slc-cache-short.md in the CC project):
- TechPowerUp, WD Black SN7100 2 TB, write test on an empty drive: ~5 GB/s until a ~648 GB
  SLC cache fills, then ~800 MB/s.
- TLC = 3 bits per cell (8 voltage levels); SLC mode = 1 bit (2 levels), so the same cells
  hold 3x less in the fast mode. Dynamic cache size depends on how full the drive is (Igor's Lab).
- The drive moves cached data into TLC when idle, freeing the cache.
Build: python -m studio.make videos/2026-11-18-ssd-slc-cache
"""
import math
import random

import skia

from studio import *

VIDEO = Video("ssd-slc-cache-v2", format="short",
              question="How full is your drive right now?")

WATER_TOP = "#7FD8EE"
WATER_BOT = "#2C7FA0"
FAST = GOLD


# ------------------------------------------------------------------ helpers
def glass_path(x, y, w, h):
    """A tumbler: slightly narrower at the bottom. (x, y) = top-left of the rim."""
    inset = w * 0.09
    p = skia.Path()
    p.moveTo(x, y)
    p.lineTo(x + inset, y + h - 14)
    p.quadTo(x + inset + 2, y + h, x + inset + 16, y + h)
    p.lineTo(x + w - inset - 16, y + h)
    p.quadTo(x + w - inset - 2, y + h, x + w - inset, y + h - 14)
    p.lineTo(x + w, y)
    return p


def glass(c, cx, cy, w, h, level, t, color_top=WATER_TOP, color_bot=WATER_BOT, marks=0,
          mark_labels=None, wave=1.0, alpha=1.0, highlight_mark=None, glow=0.0):
    """Draw a glass centred on (cx, cy) filled to `level` (0..1) with a moving water surface."""
    x, y = cx - w / 2, cy - h / 2
    outline = glass_path(x, y, w, h)
    closed = skia.Path(outline)
    closed.close()
    # glass body (faint)
    c.drawPath(closed, paint("#FFFFFF", 0.04 * alpha))
    level = clamp(level)
    if level > 0.002:
        c.save()
        c.clipPath(closed, skia.ClipOp.kIntersect, True)
        surf = y + h - level * h
        amp = 6 * wave * min(1, level * 8)
        wp = skia.Path()
        wp.moveTo(x - 10, y + h + 10)
        n = 24
        for i in range(n + 1):
            xx = x - 10 + (w + 20) * i / n
            yy = surf + amp * math.sin(i / n * 2 * math.pi * 1.3 + t * 4.2) \
                + amp * 0.5 * math.sin(i / n * 2 * math.pi * 2.7 - t * 3.1)
            wp.lineTo(xx, yy)
        wp.lineTo(x + w + 10, y + h + 10)
        wp.close()
        shader = skia.GradientShader.MakeLinear(
            [skia.Point(0, surf), skia.Point(0, y + h)],
            [rgba(color_top, alpha), rgba(color_bot, alpha)])
        pt = skia.Paint(AntiAlias=True)
        pt.setShader(shader)
        if glow > 0:
            c.drawPath(wp, paint(color_top, 0.5 * alpha * glow, blur=26))
        c.drawPath(wp, pt)
        # surface sheen
        c.drawLine(x, surf, x + w, surf, paint("#FFFFFF", 0.35 * alpha, stroke=True, width=3))
        # bubbles
        rnd = random.Random(int(cx * 7 + cy))
        for k in range(5):
            bx = x + w * (0.2 + 0.6 * rnd.random())
            speed = 40 + 50 * rnd.random()
            span = max(1, level * h - 20)
            by = y + h - 10 - ((t * speed + rnd.random() * 300) % span)
            circle(c, bx, by, 3 + 3 * rnd.random(), stroke="#FFFFFF", width=2, alpha=0.35 * alpha)
        c.restore()
    # measuring lines
    for i in range(1, marks):
        yy = y + h - i * h / marks
        hot = highlight_mark is not None and i == highlight_mark
        col = GOLD if hot else WHITE
        c.drawLine(x + w * 0.62, yy, x + w * 0.93, yy, paint(col, (0.9 if hot else 0.45) * alpha,
                                                             stroke=True, width=4 if hot else 3))
    if mark_labels:
        for i, lab in enumerate(mark_labels):
            yy = y + h - (i + 0.5) * h / len(mark_labels)
            hot = highlight_mark is not None and i == highlight_mark
            text(c, lab, x + w + 26, yy, size=34, color=GOLD if hot else GREY, weight="bold",
                 align="left", alpha=alpha)
    # outline + highlight streak
    c.drawPath(outline, paint("#CFE8F2", 0.85 * alpha, stroke=True, width=5))
    c.drawLine(x + w * 0.12, y + 18, x + w * 0.17, y + h - 30, paint("#FFFFFF", 0.12 * alpha, stroke=True, width=8))


def pour(c, x, top, bottom, t, alpha=1.0, width=14):
    """A falling stream of water from (x, top) to (x, bottom)."""
    if bottom <= top:
        return
    wob = 2.5 * math.sin(t * 20)
    shader = skia.GradientShader.MakeLinear([skia.Point(0, top), skia.Point(0, bottom)],
                                            [rgba(WATER_TOP, 0.9 * alpha), rgba(WATER_BOT, 0.9 * alpha)])
    p = skia.Paint(AntiAlias=True)
    p.setShader(shader)
    c.drawRoundRect(skia.Rect.MakeLTRB(x - width / 2 + wob, top, x + width / 2 + wob, bottom), width / 2, width / 2, p)


def splash(c, x, y, t0, t, alpha=1.0, n=7, seed=1):
    """Droplets thrown up from (x, y) at time t0."""
    s = t - t0
    if s < 0 or s > 0.6:
        return
    rnd = random.Random(seed)
    for i in range(n):
        ang = -math.pi / 2 + (rnd.random() - 0.5) * 2.0
        v = 260 + 200 * rnd.random()
        dx = math.cos(ang) * v * s
        dy = math.sin(ang) * v * s + 0.5 * 1400 * s * s
        circle(c, x + dx, y + dy, 5 + 3 * rnd.random(), fill=WATER_TOP, alpha=alpha * (1 - s / 0.6))


def speed_gauge(c, cx, cy, r, value, vmax=5000, color=GOLD, alpha=1.0):
    """A half-circle speedometer with a needle."""
    start, sweep = 180, 180
    rect_ = skia.Rect.MakeLTRB(cx - r, cy - r, cx + r, cy + r)
    bg = paint(DIM, alpha, stroke=True, width=26)
    c.drawArc(rect_, start, sweep, False, bg)
    k = clamp(value / vmax)
    fg = paint(color, alpha, stroke=True, width=26)
    c.drawArc(rect_, start, sweep * k, False, fg)
    ang = math.radians(start + sweep * k)
    line(c, cx, cy, cx + (r - 40) * math.cos(ang), cy + (r - 40) * math.sin(ang), color=WHITE, width=8, alpha=alpha)
    circle(c, cx, cy, 14, fill=WHITE, alpha=alpha)


# ------------------------------------------------------------------ 1. hook: the copy window
@VIDEO.scene("hook", lines=[
    Line("This SSD writes five thousand megabytes a second.",
         show="This SSD writes 5,000 megabytes a second."),
    Line("Copy something huge, and it crashes to eight hundred. Why?",
         show="Copy something huge, and it crashes to 800. Why?"),
], pad_in=0.1, sfx=[("whoosh", 0.0), ("pop", "five"), ("riser", ("copy", 0.0)), ("hit", "crashes"),
                     ("ding", "why")])
def hook(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    # a copy window
    wx, wy, ww, wh = 90, f.top + 90, 900, 640
    a = f.p(0.0, 0.5, "out")
    with moved(c, dy=(1 - a) * 60, alpha=a):
        rect(c, wx, wy, ww, wh, fill="#161B23", stroke="#2E3644", width=3, radius=26)
        text(c, "Copying 700 GB…", wx + 40, wy + 70, size=46, color=WHITE, weight="bold", align="left")
        text(c, "TechPowerUp test · 2 TB WD Black SN7100", wx + 40, wy + 130, size=30, color=GREY,
             weight="medium", align="left")
        # live graph
        gx0, gx1 = wx + 40, wx + ww - 40
        gy0, gy1 = wy + 520, wy + 250   # 0 and 5000 MB/s
        rect(c, gx0, gy1 - 20, gx1 - gx0, gy0 - gy1 + 20, fill="#10151C", radius=12)
        # time axis: 0..1 of the copy; the cache runs out at 648/700
        crash_at = f.cue("crashes")
        # the graph reaches the cliff exactly as "crashes" is said
        prog = 0.925 * clamp((f.t - 0.4) / (crash_at - 0.4)) + 0.075 * clamp((f.t - crash_at) / 1.4)
        cliff = 0.925
        pts = []
        N = 80
        for i in range(N + 1):
            u = prog * i / N
            v = 5000 if u < cliff else 800
            jitter = 90 * math.sin(i * 1.7) * math.sin(i * 0.37) if u < cliff else 40 * math.sin(i * 2.3)
            pts.append((lerp(gx0, gx1, u), lerp(gy0, gy1, (v + jitter) / 5000)))
        if prog > 0.01:
            area = polyline(pts + [(pts[-1][0], gy0), (gx0, gy0)], closed=True)
            sh = skia.GradientShader.MakeLinear([skia.Point(0, gy1), skia.Point(0, gy0)],
                                                [rgba(GOLD, 0.45), rgba(GOLD, 0.02)])
            pa = skia.Paint(AntiAlias=True)
            pa.setShader(sh)
            c.drawPath(area, pa)
            stroke_path(c, polyline(pts), color=GOLD if prog < cliff else RED, width=6)
        # progress bar
        rect(c, gx0, wy + 575, gx1 - gx0, 26, fill=DIM, radius=13)
        rect(c, gx0, wy + 575, (gx1 - gx0) * prog, 26, fill=BLUE, radius=13)
    # the big number
    up = f.p("five", 0.8, "out")
    down = f.p("crashes", 0.45, "in")
    if up > 0:
        v = lerp(lerp(0, 5000, up), 800, down)
        col = lerp_color(GOLD, RED, down)
        shake = 12 * math.sin(f.t * 70) * max(0, 1 - f.since("crashes") * 2.5) if f.after("crashes") else 0
        with moved(c, dx=shake):
            number(c, v, f.cx, f.top + 860, fmt="{:,.0f} MB/s", size=130, color=col, glow=8)
    w = f.p("why", 0.45, "overshoot")
    if w > 0:
        with moved(c, scale=max(w, 0.001), about=(f.cx, f.bottom - 90)):
            text(c, "WHY?", f.cx, f.bottom - 90, size=120, color=WHITE, weight="extrabold")


# ------------------------------------------------------------------ 2. cells are glasses
@VIDEO.scene("cells", lines=[
    Line("Inside, your data lives in billions of tiny cells."),
    Line("Picture each cell as a glass of water."),
], sfx=[("whoosh", 0.0), ("swell", "picture"), ("pop", "glass")])
def cells(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    # zoom from a chip full of cells into one glass
    z = f.p("picture", 1.4, "smooth")
    cx, cy = f.cx, f.cy - 60
    a = f.p(0.0, 0.6)
    # the chip with a grid of tiny glowing cells
    with moved(c, scale=1 + 5 * z * z, about=(cx, cy), alpha=a * (1 - clamp(z * 1.6))):
        box(c, cx, cy, 640, 640, fill="#1A2029", stroke=BLUE, width=5, radius=20)
        n = 14
        for i in range(n):
            for j in range(n):
                x = cx - 280 + i * 560 / (n - 1)
                y = cy - 280 + j * 560 / (n - 1)
                lit = (i * 7 + j * 13 + int(f.t * 6)) % 9 == 0
                circle(c, x, y, 11, fill=GOLD if lit else BLUE, alpha=0.9 if lit else 0.35)
        text(c, "NAND flash", cx, cy + 380, size=46, color=GREY, weight="bold")
    # one glass appears
    g = clamp((z - 0.45) / 0.55)
    if g > 0:
        with moved(c, scale=0.6 + 0.4 * overshoot(g), about=(cx, cy), alpha=g):
            glass(c, cx, cy, 300, 440, 0.0, f.t)
            text(c, "1 cell", cx, cy + 300, size=56, color=WHITE, weight="bold")
    if f.after("billions"):
        k = f.p("billions", 0.5) * (1 - z)
        text(c, "billions of cells", cx, f.top + 60, size=58, color=GOLD, weight="bold", alpha=k)


# ------------------------------------------------------------------ 3. the careful way: 3 bits
LABELS8 = ["000", "001", "010", "011", "100", "101", "110", "111"]


@VIDEO.scene("careful", lines=[
    Line("Normally, one glass stores three bits, by filling it to one of eight exact lines.",
         show="Normally, one glass stores 3 bits, by filling it to one of 8 exact lines."),
    Line("Hitting the right line takes slow, careful pouring."),
], sfx=[("pop", "three"), ("tick", "eight"), ("tick", "slow"), ("tick", ("slow", 0.6)), ("ding", ("pouring", 0.5))])
def careful(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    cx, cy, w, h = f.cx - 70, f.cy - 40, 340, 720
    target_i = 5                         # "101"
    target = (target_i + 0.5) / 8
    # level creeps up in small steps, overshoots a touch, settles
    s = f.since("hitting") if f.after("hitting") else 0
    steps = int(s / 0.32)
    lvl = 0.0
    if f.after("hitting"):
        lvl = target * (1 - 0.72 ** (steps + 1))
        lvl = min(lvl, target)
        if f.after(("pouring", 0.4)):
            lvl = target
    lab_a = f.p("eight", 0.8)
    hot = target_i if f.after(("pouring", 0.4)) else None
    glass(c, cx, cy, w, h, lvl, f.t, marks=8, mark_labels=[l if lab_a > i / 8 else "" for i, l in enumerate(LABELS8)],
          highlight_mark=hot)
    # the pour, in drips
    if f.after("hitting") and not f.after(("pouring", 0.4)):
        on = (s % 0.32) < 0.16
        if on:
            pour(c, cx, f.top + 20, cy + h / 2 - lvl * h, f.t, width=10)
    # header
    k = f.p("three", 0.5, "overshoot")
    if k > 0:
        with moved(c, scale=max(k, 0.001), about=(f.cx, f.top + 40)):
            runs(c, [("3 bits", BLUE), (" = 8 levels", WHITE)], f.cx, f.top + 40, size=72, weight="extrabold")
    sl = f.p("slow", 0.4)
    if sl > 0:
        # a little stopwatch
        sx, sy = f.cx + 330, f.bottom - 120
        circle(c, sx, sy, 60, stroke=RED, width=6, alpha=sl)
        ang = -math.pi / 2 + f.since("slow") * 2.2
        line(c, sx, sy, sx + 44 * math.cos(ang), sy + 44 * math.sin(ang), color=RED, width=6, alpha=sl)
        text(c, "slow", sx - 90, sy, size=58, color=RED, weight="extrabold", align="right", alpha=sl)


# ------------------------------------------------------------------ 4. the cheat: 1 bit
BITS = [1, 0, 1, 1, 0, 1]


@VIDEO.scene("cheat", lines=[
    Line("So at first, your SSD cheats."),
    Line("It fills each glass just empty or full. One bit. Super fast.",
         show="It fills each glass just empty or full. 1 bit. Super fast."),
], sfx=[("whoosh", "cheats"), ("pop", "empty"), ("pop", "full"), ("riser", ("one", -0.3)), ("hit", "fast")])
def cheat(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    text(c, "1 bit = empty or full", f.cx, f.top + 60, size=68, color=GOLD, weight="extrabold",
         alpha=f.p("cheats", 0.5))
    start = f.cue("fills")
    gap = 0.22
    for i, b in enumerate(BITS):
        r, k = divmod(i, 3)
        x = f.cx - 300 + k * 300
        y = f.top + 370 + r * 430
        ti = start + i * gap
        fill = f.p(ti, 0.18, "out") * b
        appear = f.p(("cheats", -0.2 + i * 0.05), 0.4, "overshoot")
        with moved(c, scale=max(appear, 0.001), about=(x, y)):
            glass(c, x, y, 190, 300, fill * 0.92, f.t + i, color_top="#FFE680", color_bot="#C9A21E",
                  glow=fill if b else 0)
            if b and f.after(ti):
                pour(c, x, f.top + 140 if r == 0 else y - 330, y - 150 + (1 - fill) * 276, f.t, alpha=1 - f.p(ti + 0.15, 0.1))
                splash(c, x, y - 150 + 30, ti + 0.12, f.t, seed=i)
            lab = str(b) if f.after(ti) else ""
            text(c, lab, x, y + 210, size=72, color=GOLD if b else GREY, weight="extrabold")
    q = f.p("fast", 0.4, "overshoot")
    if q > 0:
        with moved(c, scale=max(q, 0.001), about=(f.cx, f.bottom - 30)):
            text(c, "FAST LANE", f.cx, f.bottom - 30, size=80, color=GOLD, weight="extrabold", glow=12)


# ------------------------------------------------------------------ 5. it runs out
@VIDEO.scene("runs_out", lines=[
    Line("But that takes three glasses to hold what one could.",
         show="But that takes 3 glasses to hold what 1 could."),
    Line("So the fast lane fills up, and the speed drops.",
         show="So the fast lane fills up, and the speed drops."),
], sfx=[("pop", "three"), ("tick", "one"), ("riser", ("fast", -0.2)), ("hit", "drops")])
def runs_out(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    # three 1-bit glasses = one 3-bit glass
    a = f.p("three", 0.6)
    y = f.top + 210
    for i in range(3):
        x = 170 + i * 150
        with moved(c, alpha=a, scale=0.98 + 0.02 * a, about=(x, y)):
            glass(c, x, y, 110, 180, 0.9 if BITS[i] else 0.0, f.t + i, color_top="#FFE680", color_bot="#C9A21E")
    b = f.p("one", 0.6)
    text(c, "=", 640, y, size=110, color=WHITE, weight="bold", alpha=b)
    if b > 0:
        glass(c, 840, y, 150, 220, (5 + 0.5) / 8, f.t, marks=8, alpha=b)
    text(c, "3 bits, fast", 320, y + 150, size=38, color=GOLD, weight="bold", alpha=a)
    text(c, "3 bits, packed", 840, y + 150, size=38, color=BLUE, weight="bold", alpha=b)
    # the fast lane tank fills, the speed gauge falls
    fill_start = f.cue("fast")
    fill_end = f.cue("drops")
    lane = clamp((f.t - fill_start + 0.6) / (fill_end - fill_start + 0.6))
    k = f.p(("fast", -0.6), 0.5)
    if k > 0:
        ty = f.top + 560
        rect(c, 110, ty, 860, 80, stroke=GOLD, width=4, radius=40, alpha=k)
        rect(c, 116, ty + 6, 848 * smooth(lane), 68, fill=GOLD, radius=34, alpha=k)
        text(c, "fast lane", f.cx, ty - 40, size=40, color=GOLD, weight="bold", alpha=k)
        if lane >= 1:
            text(c, "FULL", f.cx, ty + 40, size=48, color=BG, weight="extrabold")
        drop = f.p("drops", 0.6, "in")
        v = lerp(5000, 800, drop)
        col = lerp_color(GOLD, RED, drop)
        speed_gauge(c, f.cx, f.top + 1030, 250, v, color=col, alpha=k)
        number(c, v, f.cx, f.top + 1110, fmt="{:,.0f} MB/s", size=80, color=col, alpha=k)


# ------------------------------------------------------------------ 6. it comes back
@VIDEO.scene("comes_back", lines=[
    Line("When you stop, it tidies up in the background, and the fast lane comes back."),
    Line("And the emptier your drive, the bigger that fast lane."),
], sfx=[("whoosh", "tidies"), ("swell", "comes"), ("ding", "back"), ("pop", "emptier")])
def comes_back(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    y = f.top + 260
    # three gold glasses pour into one blue packed glass
    m = f.p("tidies", 2.0)
    for i in range(3):
        x = 170 + i * 150
        lvl = 0.9 * (1 - clamp(m * 3 - i)) if BITS[i] else 0
        glass(c, x, y, 110, 180, lvl, f.t + i, color_top="#FFE680", color_bot="#C9A21E")
        if BITS[i] and 0 < m * 3 - i < 1:
            pour(c, x + 60, y - 60, y + 90, f.t, width=8)
    glass(c, 840, y, 150, 220, (5 + 0.5) / 8 * smooth(m), f.t, marks=8)
    arrow(c, 560, y, 730, y, color=WHITE, width=6, progress=f.p("tidies", 0.6))
    # the fast lane refills (empties of data, ready again)
    ty = f.top + 560
    back = smooth(m)
    rect(c, 110, ty, 860, 80, stroke=GOLD, width=4, radius=40)
    if back < 0.99:
        rect(c, 116, ty + 6, 848 * (1 - back), 68, fill=GOLD, radius=34)
    ready = f.p("back", 0.4, "overshoot")
    text(c, "fast lane full", f.cx, ty - 40, size=40, color=GOLD, weight="bold", alpha=1 - ready)
    if ready > 0:
        with moved(c, scale=max(ready, 0.001), about=(f.cx, ty + 40)):
            text(c, "READY", f.cx, ty + 40, size=50, color=GOLD, weight="extrabold", glow=8)
    # drive fullness vs fast-lane size
    e = f.p("emptier", 0.6)
    if e > 0:
        for j, (used, lab) in enumerate([(0.2, "20% full"), (0.85, "85% full")]):
            by = f.top + 830 + j * 220
            rect(c, 110, by, 860, 70, fill=DIM, radius=14, alpha=e)
            rect(c, 110, by, 860 * used * e, 70, fill=GREY, radius=14, alpha=e)
            lane_w = 860 * (1 - used) / 3 * e        # at most ~1/3 of free space
            rect(c, 110 + 860 * used, by, lane_w, 70, fill=GOLD, radius=14, alpha=e * (0.9 + 0.1 * pulse(f.t)))
            text(c, lab, 110, by - 34, size=36, color=WHITE, weight="bold", align="left", alpha=e)
            text(c, "big fast lane" if used < 0.5 else "tiny fast lane", 970, by - 34, size=36,
                 color=GOLD, weight="bold", align="right", alpha=e)
