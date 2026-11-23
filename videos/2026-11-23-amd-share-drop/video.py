"""Short: AMD tops the gaming charts, yet lost 5 points of desktop CPU share in Q3 2026.

Lane: proven (hardware, CPUs). Made at the 11 AM IST auto-check, Nov 23, 2026.

Facts (see claude/amd-share-drop-short.md in the CC project):
- Mercury Research, Q3 2026 (July-September), desktop x86 unit share: Intel 65.1% -> 70.1%,
  AMD 34.9% -> 29.9% (Hardware Busters, Nov 14, 2026; PC Gamer, Nov 13, 2026).
  AMD was 32.2% a year earlier and 33.2% in Q1 2026.
- Mercury: desktop x86 shipments down more than 20% both year on year and quarter on quarter.
- Mercury's working theory (not certain): Intel moved spare supply from weak laptop demand into
  desktops; AMD has greater exposure to PC gaming, which suffered from constrained gaming-GPU
  supply. PC Gamer's author points to absurd GPU, RAM and storage prices instead.
- Share counts units shipped, so every desktop chip counts once, whatever it is used for.
Build: python -m studio.make videos/2026-11-23-amd-share-drop
"""
import math
import random

import skia

from studio import *

VIDEO = Video("amd-share-drop", format="short", speed=1.1,
              question="Did GPU and RAM prices stop your PC build this year?")

AMDC = RED
INTC = BLUE
PANEL = "#161B23"


# ------------------------------------------------------------------ helpers
def pie(c, cx, cy, r, amd_share, alpha=1.0, labels=True, lsize=56):
    """Two-slice pie: AMD (red) from 12 o'clock clockwise, Intel (blue) for the rest."""
    oval = skia.Rect.MakeLTRB(cx - r, cy - r, cx + r, cy + r)
    a_sweep = 360 * amd_share
    pa = paint(AMDC, alpha)
    pi_ = paint(INTC, alpha)
    p = skia.Path()
    p.moveTo(cx, cy)
    p.arcTo(oval, -90, a_sweep, False)
    p.close()
    c.drawPath(p, pa)
    p2 = skia.Path()
    p2.moveTo(cx, cy)
    p2.arcTo(oval, -90 + a_sweep, 360 - a_sweep, False)
    p2.close()
    c.drawPath(p2, pi_)
    # thin gap lines
    for ang in (-90, -90 + a_sweep):
        rad = math.radians(ang)
        line(c, cx, cy, cx + r * math.cos(rad), cy + r * math.sin(rad), color=BG, width=6, alpha=alpha)
    if labels and r > 120:
        ma = math.radians(-90 + a_sweep / 2)
        text(c, f"{amd_share * 100:.1f}%", cx + r * 0.58 * math.cos(ma), cy + r * 0.58 * math.sin(ma),
             size=lsize, color=WHITE, weight="extrabold", alpha=alpha)
        mi = math.radians(-90 + a_sweep + (360 - a_sweep) / 2)
        text(c, f"{(1 - amd_share) * 100:.1f}%", cx + r * 0.55 * math.cos(mi), cy + r * 0.55 * math.sin(mi),
             size=lsize, color=BG, weight="extrabold", alpha=alpha)


def legend(c, x, y, alpha=1.0, size=40):
    rect(c, x, y - 16, 32, 32, fill=AMDC, radius=6, alpha=alpha)
    text(c, "AMD", x + 48, y, size=size, color=WHITE, weight="bold", align="left", alpha=alpha)
    rect(c, x + 200, y - 16, 32, 32, fill=INTC, radius=6, alpha=alpha)
    text(c, "Intel", x + 248, y, size=size, color=WHITE, weight="bold", align="left", alpha=alpha)


def pc_tower(c, cx, cy, s=1.0, color=GREY, alpha=1.0, accent=None):
    w, h = 150 * s, 230 * s
    box(c, cx, cy, w, h, fill=PANEL, stroke=color, width=4, radius=14 * s, alpha=alpha)
    for i in range(3):
        circle(c, cx, cy - 60 * s + i * 55 * s, 18 * s, stroke=accent or color, width=3, alpha=alpha * 0.8)
    rect(c, cx - w / 2 + 16 * s, cy + h / 2 - 30 * s, w - 32 * s, 10 * s, fill=color, radius=4, alpha=alpha * 0.6)


def laptop(c, cx, cy, s=1.0, color=GREY, alpha=1.0):
    box(c, cx, cy - 40 * s, 220 * s, 140 * s, fill=PANEL, stroke=color, width=4, radius=10, alpha=alpha)
    box(c, cx, cy + 42 * s, 260 * s, 22 * s, fill=color, radius=8, alpha=alpha * 0.8)


def price_tag(c, x, y, label, k, color=GOLD, alpha=1.0):
    with moved(c, scale=max(k, 0.001), about=(x, y), alpha=alpha):
        box(c, x, y, 270, 90, fill=PANEL, stroke=color, width=4, radius=16)
        circle(c, x - 108, y, 9, fill=color)
        text(c, label, x + 16, y, size=40, color=color, weight="extrabold")


# ------------------------------------------------------------------ 1. hook
@VIDEO.scene("hook", lines=[
    Line("AMD's X three D chips top most gaming charts.",
         show="AMD's X3D chips top most gaming charts."),
    Line("Yet in three months, its desktop share fell from thirty-five percent to thirty.",
         show="Yet in 3 months, its desktop share fell from 35% to 30%."),
], pad_in=0.1, sfx=[("whoosh", 0.0), ("ding", "charts"), ("riser", ("fell", -0.4)), ("hit", "thirty")])
def hook(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    # gaming chart: AMD bar on top, fades back when the pie arrives
    fade = 1 - f.p(("yet", -0.1), 0.5)
    a = f.p(0.0, 0.5, "out")
    if fade > 0.01:
        y0 = f.top + 120
        text(c, "GAMING FPS CHART", f.cx, y0, size=52, color=GREY, weight="extrabold", alpha=a * fade)
        rows = [("AMD X3D", 1.0, AMDC), ("CPU B", 0.86, DIM), ("CPU C", 0.8, DIM), ("CPU D", 0.72, DIM)]
        for i, (lab, v, col) in enumerate(rows):
            k = f.p(0.15 + i * 0.12, 0.6, "out")
            y = y0 + 110 + i * 130
            text(c, lab, 110, y + 40, size=40, color=WHITE if i == 0 else GREY, weight="bold", align="left",
                 alpha=k * fade)
            rect(c, 340, y + 8, 620 * v * k, 64, fill=col, radius=10, alpha=fade)
        tk = f.p("top", 0.5, "overshoot")
        if tk > 0:
            with moved(c, scale=max(tk, 0.001), about=(f.cx, y0 + 760), alpha=fade):
                text(c, "#1", f.cx, y0 + 760, size=170, color=GOLD, weight="extrabold", glow=8)
        text(c, "illustration", f.cx, y0 + 900, size=28, color=GREY, weight="medium", alpha=a * fade * 0.8)
    # the pie: 34.9 -> 29.9
    b = f.p(("yet", -0.1), 0.6, "out")
    if b > 0:
        cx, cy = f.cx, f.top + 520
        k = f.p(("fell", 0.1), 1.4, "smooth")
        share = lerp(0.349, 0.299, k)
        with moved(c, scale=lerp(0.6, 1.0, b), about=(cx, cy), alpha=b):
            text(c, "DESKTOP CPUs SHIPPED", cx, f.top + 70, size=50, color=WHITE, weight="extrabold")
            pie(c, cx, cy, 330, share)
            legend(c, cx - 200, cy + 400)
        h = f.p("thirty", 0.5, "overshoot")
        if h > 0:
            with moved(c, scale=max(h, 0.001), about=(f.cx, f.top + 1040)):
                runs(c, [("35%", GREY), ("  →  ", GREY), ("30%", AMDC)], f.cx, f.top + 1040, size=110,
                     weight="extrabold")


# ------------------------------------------------------------------ 2. Intel up
@VIDEO.scene("intel", lines=[
    Line("Intel went from sixty-five to seventy percent.",
         show="Intel went from 65% to 70%."),
    Line("Mercury Research, July to September."),
], sfx=[("pop", "sixty-five"), ("hit", "seventy"), ("tick", "mercury")])
def intel(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    a = f.p(0.0, 0.4)
    base = f.top + 820
    k1 = f.p(("sixty-five", -0.1), 0.6, "out")
    k2 = f.p(("seventy", -0.1), 0.8, "overshoot")
    text(c, "INTEL · DESKTOP SHARE", f.cx, f.top + 60, size=50, color=INTC, weight="extrabold", alpha=a)
    bar(c, 330, base, 220, 6.5 * 65.1, color=DIM, progress=k1, label="Apr–Jun", value="65.1%",
        value_size=60)
    bar(c, 750, base, 220, 6.5 * 70.1, color=INTC, progress=k2, label="Jul–Sep", value="70.1%",
        value_size=60, value_color=INTC)
    if k2 > 0.5:
        arrow(c, 450, base - 470, 630, base - 510, color=GOLD, width=6, progress=f.p("seventy", 0.5))
        text(c, "+5 points", 540, base - 580, size=48, color=GOLD, weight="extrabold", alpha=f.p("seventy", 0.5))
    m = f.p("mercury", 0.5, "out")
    if m > 0:
        with moved(c, dy=(1 - m) * 40, alpha=m):
            box(c, f.cx, f.top + 1000, 900, 150, fill=PANEL, stroke=GREY, width=3, radius=20)
            text(c, "Mercury Research · Q3 2026", f.cx, f.top + 975, size=44, color=WHITE, weight="bold")
            text(c, "desktop x86 units · via PC Gamer, Hardware Busters", f.cx, f.top + 1030, size=30,
                 color=GREY, weight="medium")


# ------------------------------------------------------------------ 3. one chip, one vote
@VIDEO.scene("vote", lines=[
    Line("But share doesn't count benchmarks. It counts chips shipped."),
    Line("Office, school, gaming: one chip, one vote."),
], sfx=[("tick", "benchmarks"), ("pop", "office"), ("pop", "school"), ("pop", "gaming"), ("ding", "vote")])
def vote(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    # benchmark crossed out, then a box counting chips
    a = f.p(0.0, 0.4)
    y = f.top + 80
    text(c, "FPS", f.cx - 220, y, size=80, color=GREY, weight="extrabold", alpha=a)
    s = f.p(("benchmarks", 0.2), 0.4)
    line(c, f.cx - 320, y + 5, f.cx - 120, y + 5, color=RED, width=10, progress=s)
    k = f.p("chips", 0.5, "overshoot")
    if k > 0:
        with moved(c, scale=max(k, 0.001), about=(f.cx + 200, y)):
            text(c, "UNITS", f.cx + 200, y, size=80, color=GOLD, weight="extrabold", glow=6)
    # three PCs drop a chip each into a counter
    items = [("office", "office", f.cx - 330, INTC), ("school", "school", f.cx, INTC),
             ("gaming", "gaming", f.cx + 330, AMDC)]
    count = 0
    for cue, lab, x, col in items:
        p = f.p(cue, 0.45, "overshoot")
        if p <= 0:
            continue
        with moved(c, scale=max(p, 0.001), about=(x, f.top + 420)):
            pc_tower(c, x, f.top + 420, s=0.9, color=col)
            text(c, lab, x, f.top + 580, size=40, color=WHITE, weight="bold")
        d = f.p((cue, 0.35), 0.6, "in")
        if d > 0:
            cy_ = lerp(f.top + 420, f.top + 850, d)
            cx_ = lerp(x, f.cx, d)
            if d < 1:
                box(c, cx_, cy_, 56, 56, fill=col, radius=8)
            else:
                count += 1
    box(c, f.cx, f.top + 900, 420, 150, fill=PANEL, stroke=GOLD, width=4, radius=20, alpha=f.p("office", 0.4))
    text(c, f"chips: {count}", f.cx, f.top + 900, size=64, color=GOLD, weight="extrabold", alpha=f.p("office", 0.4))
    v = f.p("vote", 0.5, "overshoot")
    if v > 0:
        with moved(c, scale=max(v, 0.001), about=(f.cx, f.top + 1080)):
            text(c, "1 chip = 1 vote", f.cx, f.top + 1080, size=70, color=WHITE, weight="extrabold")


# ------------------------------------------------------------------ 4. the pie shrank
@VIDEO.scene("shrink", lines=[
    Line("And the whole pie shrank. Desktop shipments fell more than twenty percent.",
         show="And the whole pie shrank. Desktop shipments fell more than 20%."),
], sfx=[("whoosh", "shrank"), ("hit", "twenty")])
def shrink(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    a = f.p(0.0, 0.4)
    k = f.p("shrank", 1.2, "smooth")
    r0 = 340
    r = r0 * math.sqrt(lerp(1.0, 0.78, k))   # area ~ shipments; "more than 20%" drawn as 22%
    cx, cy = f.cx, f.top + 470
    circle(c, cx, cy, r0, stroke=GREY, width=3, alpha=a * 0.5 * k)
    pie(c, cx, cy, r, 0.299, alpha=a, labels=False)
    text(c, "last year's pie", cx + r0 * 0.45, cy - r0 - 30, size=32, color=GREY, weight="medium",
         alpha=a * k * 0.9)
    h = f.p("twenty", 0.5, "overshoot")
    if h > 0:
        with moved(c, scale=max(h, 0.001), about=(f.cx, f.top + 950)):
            text(c, "−20%+", f.cx, f.top + 950, size=150, color=GOLD, weight="extrabold", glow=8)
    text(c, "desktop x86 shipments, vs a year ago and vs last quarter", f.cx, f.top + 1080, size=30,
         color=GREY, weight="medium", alpha=h)


# ------------------------------------------------------------------ 5. theory 1: laptop chips -> desktops
@VIDEO.scene("moved", lines=[
    Line("Mercury's guess? Laptop sales were weak, so Intel moved spare chips into desktops."),
], sfx=[("tick", "guess"), ("pop", "weak"), ("whoosh", "moved"), ("ding", "desktops")])
def moved_chips(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    a = f.p(0.0, 0.4)
    text(c, "THEORY 1 (Mercury Research)", f.cx, f.top + 50, size=44, color=GREY, weight="extrabold", alpha=a)
    lx, dx, y = 270, 810, f.top + 430
    laptop(c, lx, y, s=1.2, alpha=a)
    text(c, "laptops", lx, y + 150, size=44, color=WHITE, weight="bold", alpha=a)
    w = f.p("weak", 0.5)
    text(c, "demand ↓", lx, y + 215, size=40, color=RED, weight="extrabold", alpha=w)
    pc_tower(c, dx, y, s=1.2, color=GREY, alpha=a)
    text(c, "desktops", dx, y + 190, size=44, color=WHITE, weight="bold", alpha=a)
    # spare chips pile up, then fly over
    rnd = random.Random(3)
    t0 = f.cue("moved")
    for i in range(10):
        sx = lx - 150 + (i % 5) * 70
        sy = y + 330 + (i // 5) * 70
        appear = f.p(("weak", 0.1 + 0.05 * i), 0.3, "overshoot")
        if appear <= 0:
            continue
        fly = clamp((f.t - t0 - 0.07 * i) / 0.8) if f.after("moved") else 0.0
        fly = smooth(fly)
        ex = dx - 150 + (i % 5) * 70 + rnd.uniform(-4, 4)
        ey = y + 330 + (i // 5) * 70
        x = lerp(sx, ex, fly)
        yy = lerp(sy, ey, fly) - 260 * math.sin(math.pi * fly)
        box(c, x, yy, 54 * min(appear, 1.1), 54 * min(appear, 1.1), fill=INTC, radius=8)
    text(c, "spare Intel chips", f.cx, y + 520, size=40, color=INTC, weight="bold", alpha=f.p(("weak", 0.4), 0.4))
    text(c, "a working theory, not confirmed", f.cx, f.top + 1080, size=32, color=GREY, weight="medium",
         alpha=f.p("desktops", 0.4))


# ------------------------------------------------------------------ 6. theory 2: gamers stopped building
@VIDEO.scene("gamers", lines=[
    Line("And AMD leans on gamers. With graphics cards and RAM this expensive, fewer built new PCs."),
], sfx=[("pop", "gamers"), ("tick", "graphics"), ("tick", "ram"), ("hit", "fewer")])
def gamers(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    a = f.p(0.0, 0.4)
    text(c, "THEORY 2", f.cx, f.top + 50, size=44, color=GREY, weight="extrabold", alpha=a)
    g = f.p("gamers", 0.5, "overshoot")
    if g > 0:
        with moved(c, scale=max(g, 0.001), about=(f.cx, f.top + 200)):
            box(c, f.cx, f.top + 200, 780, 110, fill=PANEL, stroke=AMDC, width=4, radius=55)
            text(c, "AMD: more exposed to PC gaming", f.cx, f.top + 200, size=38, color=WHITE, weight="bold")
    # a PC being built, parts slot in, then price tags stop it
    cy = f.top + 560
    pc_tower(c, f.cx, cy, s=1.5, color=GREY, alpha=a, accent=AMDC)
    price_tag(c, f.cx - 300, cy - 120, "GPU $$$", f.p("graphics", 0.5, "overshoot"))
    price_tag(c, f.cx + 300, cy - 120, "RAM $$$", f.p("ram", 0.5, "overshoot"))
    fw = f.p("fewer", 0.4)
    if fw > 0:
        # big red stop cross over the PC
        line(c, f.cx - 150, cy - 200, f.cx + 150, cy + 200, color=RED, width=14, progress=fw)
        line(c, f.cx + 150, cy - 200, f.cx - 150, cy + 200, color=RED, width=14, progress=f.p(("fewer", 0.15), 0.4))
        text(c, "fewer new gaming PCs", f.cx, f.top + 920, size=56, color=RED, weight="extrabold", alpha=fw)
        text(c, "fewer AMD chips shipped", f.cx, f.top + 1000, size=44, color=WHITE, weight="bold",
             alpha=f.p(("fewer", 0.4), 0.4))
    text(c, "Mercury: gaming GPU supply · PC Gamer: absurd prices", f.cx, f.top + 1090, size=28, color=GREY,
         weight="medium", alpha=f.p(("built", 0.0), 0.4))


# ------------------------------------------------------------------ 7. verdict
@VIDEO.scene("verdict", lines=[
    Line("So AMD didn't lose on speed. It may have lost because gaming PCs got too expensive."),
], sfx=[("whoosh", 0.0), ("ding", "speed"), ("hit", "expensive")], pad_out=0.4)
def verdict(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    a = f.p(0.0, 0.5, "out")
    colw = 440
    for i, (title, big, small, col, cue) in enumerate([
        ("SPEED", "AMD", "tops gaming charts", AMDC, "amd"),
        ("UNITS", "Intel", "70% of desktops", INTC, "lost"),
    ]):
        x = f.cx - 240 + i * 480
        k = f.p(cue, 0.5, "overshoot")
        if k <= 0:
            continue
        with moved(c, scale=max(k, 0.001), about=(x, f.top + 330)):
            box(c, x, f.top + 330, colw, 420, fill=PANEL, stroke=col, width=5, radius=24)
            text(c, title, x, f.top + 190, size=44, color=GREY, weight="extrabold")
            text(c, big, x, f.top + 320, size=110, color=col, weight="extrabold")
            text(c, small, x, f.top + 440, size=36, color=WHITE, weight="bold")
    e = f.p("expensive", 0.6, "overshoot")
    if e > 0:
        with moved(c, scale=max(e, 0.001), about=(f.cx, f.top + 800)):
            price_tag(c, f.cx - 220, f.top + 800, "GPU $$$", 1.0)
            price_tag(c, f.cx + 220, f.top + 800, "RAM $$$", 1.0)
        text(c, "the real opponent?", f.cx, f.top + 960, size=64, color=GOLD, weight="extrabold", glow=6,
             alpha=clamp(e))
    text(c, "as of Q3 2026 · Mercury Research", f.cx, f.top + 1080, size=30, color=GREY, weight="medium", alpha=a)
