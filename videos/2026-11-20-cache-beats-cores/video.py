"""Short: 2 more cores = ~3% more FPS; 6x the L3 cache = 45% (TechSpot Zen 3 test).

Lane: proven (hardware). Series: "Spec says X, reality says Y".

Facts (see claude/cache-beats-cores-short.md in the CC project):
- TechSpot, "CPU cache vs cores" (techspot.com/review/2811-cpu-cache-vs-cores, "early 2024"):
  Zen 3 Ryzen CPUs with 16 MB (5600G/5700G), 32 MB (5600X/5800X) and 96 MB (5600X3D/5800X3D)
  of L3, RTX 4090 at 1080p, DDR4-3600 CL14, 12-game average.
  "on average, we observed up to a 3% performance advantage when going from 6 to 8 cores."
  "By doubling the L3 cache capacity from 16MB to 32MB, we saw an average of 18% better
  performance ... going from 32MB to 96MB netted us a further 23% improvement ... a 45% uplift
  when going from 16MB to 96MB, while using the same number of Zen 3 cores."
  Watch Dogs: Legion: 6 and 8 cores identical ("extra cores don't bring benefits"), 55% from
  16 MB to 96 MB.
  Conclusion: "Cache matters. Often more so than cores, when it comes to PC gaming performance."
- 96 / 16 = 6x. The 96 MB chips are AMD's X3D parts (3D V-Cache).
- Mechanism (textbook, not from TechSpot): L3 is on the CPU; a miss goes out to system RAM,
  which takes several times longer, and the core stalls while it waits.
Build: python -m studio.make videos/2026-11-20-cache-beats-cores
"""
import math
import random

from studio import *

VIDEO = Video("cache-beats-cores", format="short", speed=1.06,
              question="More cores or more cache: what's in your PC?")

CACHE = TEAL
RAMC = PURPLE


# ------------------------------------------------------------------ helpers
def cores_grid(c, cx, cy, n, lit_n, size=70, gap=16, color=BLUE, alpha=1.0, waiting=0.0, t=0.0):
    """n cores in two rows; `waiting` turns them red and makes them pulse."""
    cols = (n + 1) // 2
    w = cols * size + (cols - 1) * gap
    x0 = cx - w / 2
    for i in range(n):
        r, k = divmod(i, cols)
        x = x0 + k * (size + gap)
        y = cy - size - gap / 2 + r * (size + gap)
        on = i < lit_n
        col = lerp_color(color, RED, waiting) if on else DIM
        a = alpha * (0.75 + 0.25 * math.sin(t * 6 + i)) if waiting > 0.5 and on else alpha
        rect(c, x, y, size, size, fill=col, radius=10, alpha=a)
        if on:
            text(c, "C", x + size / 2, y + size / 2, size=size * 0.42, color=BG, weight="extrabold", alpha=a)


def hbar(c, x, y, w, h, color, label, value, alpha=1.0, vcol=None):
    rect(c, x, y, w, h, fill=color, radius=10, alpha=alpha)
    text(c, label, x, y - 30, size=36, color=GREY, weight="bold", align="left", alpha=alpha)
    if value:
        text(c, value, x + w + 24, y + h / 2, size=64, color=vcol or color, weight="extrabold",
             align="left", alpha=alpha)


# ------------------------------------------------------------------ 1. hook
@VIDEO.scene("hook", lines=[
    Line("Two more CPU cores made games about three percent faster.",
         show="Two more CPU cores made games about 3% faster."),
    Line("Six times the cache? Forty-five percent.",
         show="6x the cache? 45%."),
], pad_in=0.1, sfx=[("whoosh", 0.0), ("pop", "two"), ("tick", "three"), ("riser", ("six", -0.3)),
                    ("hit", "forty-five")])
def hook(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    a = f.p(0.0, 0.5, "out")
    # top half: cores 6 -> 8
    y1 = f.top + 60
    text(c, "+2 CORES", f.cx, y1, size=60, color=BLUE, weight="extrabold", alpha=a)
    k = f.p("two", 0.6, "overshoot")
    lit = 6 + 2 * clamp(k)
    cores_grid(c, f.cx, y1 + 170, 8, int(round(lit)), alpha=a)
    g = f.p("three", 0.7, "out")
    if g > 0:
        hbar(c, 110, y1 + 320, 18 + 22 * g, 70, BLUE, "FPS GAIN", "+3%", alpha=g)
    # bottom half: cache 16 -> 96 MB
    b = f.p(("six", -0.2), 0.5)
    if b > 0:
        y2 = f.top + 600
        text(c, "6× CACHE", f.cx, y2, size=60, color=CACHE, weight="extrabold", alpha=b)
        grow = f.p("six", 0.9, "out")
        mb = lerp(16, 96, grow)
        cw = lerp(130, 780, grow)
        box(c, f.cx, y2 + 150, cw, 120, fill=CACHE, radius=14, alpha=b * 0.9)
        text(c, f"{mb:.0f} MB L3", f.cx, y2 + 150, size=52, color=BG, weight="extrabold",
             alpha=b * clamp((cw - 200) / 100 + 0.2))
        h = f.p("forty-five", 0.8, "overshoot")
        if h > 0:
            hbar(c, 110, y2 + 330, 40 + 560 * clamp(h, 0, 1.1), 70, GOLD, "FPS GAIN", "+45%",
                 alpha=clamp(h * 3))


# ------------------------------------------------------------------ 2. setup
@VIDEO.scene("setup", lines=[
    Line("Same Zen three cores. Same R T X forty-ninety. Twelve games.",
         show="Same Zen 3 cores. Same RTX 4090. Twelve games."),
    Line("So why does cache win so big?"),
], sfx=[("tick", "zen"), ("tick", "forty-ninety"), ("tick", "twelve"), ("swell", "why")])
def setup(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    items = [("zen", "Ryzen 5000 (Zen 3)", "6 or 8 cores", BLUE),
             ("forty-ninety", "RTX 4090 · 1080p", "same GPU", GREEN),
             ("twelve", "12 games", "average", GOLD)]
    for i, (cue, big, small, col) in enumerate(items):
        k = f.p(cue, 0.5, "out")
        y = f.top + 60 + i * 200
        with moved(c, dx=(1 - k) * 140, alpha=k):
            rect(c, 110, y, 860, 160, fill="#161B23", stroke=col, width=4, radius=20)
            text(c, big, 160, y + 60, size=50, color=col, weight="extrabold", align="left")
            text(c, small, 160, y + 118, size=34, color=GREY, weight="medium", align="left")
    text(c, "Source: TechSpot, CPU cache vs cores (2024)", f.cx, f.top + 700, size=30, color=GREY,
         weight="medium", alpha=f.p("twelve", 0.5))
    q = f.p("why", 0.5, "overshoot")
    if q > 0:
        with moved(c, scale=max(q, 0.001), about=(f.cx, f.top + 900)):
            text(c, "WHY?", f.cx, f.top + 900, size=130, color=WHITE, weight="extrabold")


# ------------------------------------------------------------------ 3. shelf vs warehouse
CORE_X, SHELF_X, RAM_X = 200, 470, 880


def scene_layout(c, f, a, shelf_w=150, shelf_label="L3 cache"):
    y = f.top + 420
    chip(c, CORE_X, y, 190, color=BLUE, label="CORE", alpha=a)
    box(c, SHELF_X, y, shelf_w, 190, fill="#13262A", stroke=CACHE, width=5, radius=14, alpha=a)
    for i in range(4):
        line(c, SHELF_X - shelf_w / 2 + 12, y - 70 + i * 46, SHELF_X + shelf_w / 2 - 12, y - 70 + i * 46,
             color=CACHE, width=3, alpha=a * 0.6)
    text(c, shelf_label, SHELF_X, y + 140, size=34, color=CACHE, weight="bold", alpha=a)
    return y


@VIDEO.scene("shelf", lines=[
    Line("Cache is a small shelf right next to the cores."),
    Line("RAM is a warehouse, far away."),
], sfx=[("whoosh", 0.0), ("pop", "shelf"), ("pop", "warehouse")])
def shelf(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    a = f.p(0.0, 0.5)
    s = f.p("shelf", 0.5, "overshoot")
    y = f.top + 420
    chip(c, CORE_X, y, 190, color=BLUE, label="CORE", alpha=a)
    if s > 0:
        with moved(c, scale=max(s, 0.001), about=(SHELF_X, y)):
            scene_layout(c, f, 1.0)
        text(c, "on the chip", (CORE_X + SHELF_X) / 2, y - 170, size=36, color=GREEN, weight="bold",
             alpha=f.p("next", 0.4))
    w = f.p("warehouse", 0.6, "overshoot")
    if w > 0:
        with moved(c, scale=max(w, 0.001), about=(RAM_X, y)):
            box(c, RAM_X, y, 220, 260, fill="#1E1726", stroke=RAMC, width=5, radius=14)
            for i in range(3):
                for j in range(3):
                    box(c, RAM_X - 60 + j * 60, y - 70 + i * 70, 44, 44, fill=RAMC, radius=6, alpha=0.7)
            text(c, "RAM", RAM_X, y + 170, size=40, color=RAMC, weight="extrabold")
        d = f.p(("far", -0.2), 0.8)
        arrow(c, SHELF_X + 90, y + 260, RAM_X - 20, y + 260, color=GREY, width=5, progress=d)
        arrow(c, RAM_X - 20, y + 260, SHELF_X + 90, y + 260, color=GREY, width=5, progress=d)
        text(c, "far away", (SHELF_X + RAM_X) / 2 + 30, y + 320, size=40, color=GREY, weight="bold", alpha=d)
        tt = f.p("far", 0.5)
        text(c, "next door", (CORE_X + SHELF_X) / 2, y + 230, size=34, color=CACHE, weight="bold", alpha=tt)
        text(c, "several times longer", f.cx + 120, y + 400, size=44, color=RAMC, weight="extrabold", alpha=tt)


# ------------------------------------------------------------------ 4. the miss
@VIDEO.scene("miss", lines=[
    Line("When the data isn't on the shelf, the core stops, and waits for the long trip."),
], sfx=[("tick", "isn't"), ("riser", "stops"), ("ding", "trip")])
def miss(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    a = f.p(0.0, 0.4)
    y = scene_layout(c, f, a)
    box(c, RAM_X, y, 220, 260, fill="#1E1726", stroke=RAMC, width=5, radius=14, alpha=a)
    text(c, "RAM", RAM_X, y + 170, size=40, color=RAMC, weight="extrabold", alpha=a)
    # a request checks the shelf: miss
    m = f.p("isn't", 0.4)
    if m > 0:
        text(c, "MISS", SHELF_X, y - 170, size=64, color=RED, weight="extrabold", alpha=m, glow=6)
    # the long trip: a packet goes to RAM and back
    t0 = f.cue("stops")
    trip = 2.4
    if f.after("stops"):
        u = clamp((f.t - t0) / trip)
        if u < 0.5:
            px = lerp(SHELF_X, RAM_X, u * 2)
        else:
            px = lerp(RAM_X, CORE_X + 100, (u - 0.5) * 2)
        box(c, px, y - 40, 50, 36, fill=GOLD if u >= 0.5 else BLUE, radius=6)
        # the core waits: a stopwatch fills
        wt = clamp((f.t - t0) / trip)
        cy2 = y + 330
        text(c, "core:", 110, cy2, size=44, color=GREY, weight="bold", align="left")
        rect(c, 250, cy2 - 32, 700, 64, stroke=DIM, width=3, radius=10)
        rect(c, 250, cy2 - 32, 700 * wt, 64, fill=RED, radius=10)
        text(c, "WAITING" if wt < 1 else "got it", 600, cy2, size=38, color=WHITE, weight="extrabold")
    # the core turns red while waiting
    if f.after("stops") and (f.t - t0) < trip:
        rect(c, CORE_X - 95, y - 95, 190, 190, stroke=RED, width=8, radius=12, alpha=0.6 + 0.4 * pulse(f.t * 3))


# ------------------------------------------------------------------ 5. games: small vs big shelf
@VIDEO.scene("games", lines=[
    Line("Games jump all over memory: enemies, physics, the world around you."),
    Line("A bigger shelf means fewer long trips."),
], sfx=[("pop", "enemies"), ("pop", "physics"), ("pop", "world"), ("whoosh", "bigger"), ("ding", "fewer")])
def games(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    words = [("enemies", "enemies", f.top + 60), ("physics", "physics", f.top + 60),
             ("world", "world", f.top + 60)]
    for i, (cue, lab, y) in enumerate(words):
        k = f.p(cue, 0.4, "overshoot")
        if k > 0:
            x = 220 + i * 320
            with moved(c, scale=max(k, 0.001), about=(x, y)):
                box(c, x, y, 260, 80, fill="#161B23", stroke=GOLD, width=3, radius=40)
                text(c, lab, x, y, size=40, color=GOLD, weight="bold")
    # requests for 24 pieces of data; a small shelf holds 4, a big one 20
    big = f.p("bigger", 0.8, "smooth")
    cap = int(round(lerp(4, 20, big)))
    rnd = random.Random(7)
    order = list(range(24))
    rnd.shuffle(order)
    held = set(order[:cap])
    y0 = f.top + 230
    text(c, "shelf", 110, y0, size=36, color=CACHE, weight="bold", align="left")
    sh_w = lerp(220, 860, big)
    rect(c, 110, y0 + 30, sh_w, 90, fill="#13262A", stroke=CACHE, width=4, radius=12)
    text(c, f"{lerp(16, 96, big):.0f} MB", 110 + sh_w - 20, y0 + 75, size=36, color=CACHE, weight="bold",
         align="right")
    # request grid
    gy = f.top + 420
    hits = 0
    shown = 0
    start = f.cue("games")
    for j in range(24):
        if f.t < start + 0.12 * j:
            continue
        appear = f.p(start + 0.12 * j, 0.25, "overshoot")
        shown += 1
        x = 170 + (j % 8) * 105
        yy = gy + (j // 8) * 105
        hit = j in held
        hits += hit
        col = GREEN if hit else RED
        circle(c, x, yy, 34 * min(appear, 1.15), fill=col, alpha=0.9)
        if hit:
            text(c, "✓", x, yy, size=34, color=BG, weight="extrabold")
        else:
            line(c, x - 12, yy - 12, x + 12, yy + 12, color=BG, width=6)
            line(c, x + 12, yy - 12, x - 12, yy + 12, color=BG, width=6)
    if shown:
        misses = shown - hits
        text(c, f"{misses} long trips", f.cx, gy + 380, size=64, color=RED if misses > 8 else GREEN,
             weight="extrabold")


# ------------------------------------------------------------------ 6. cores don't help
@VIDEO.scene("together", lines=[
    Line("More cores don't fix that. They just wait together."),
], sfx=[("pop", "more"), ("hit", "together")])
def together(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    k = f.p("more", 0.5, "overshoot")
    n = 6 + int(round(2 * clamp(k)))
    w = f.p("wait", 0.5)
    cores_grid(c, f.cx, f.top + 300, 8, n, size=100, gap=20, waiting=w, t=f.t)
    text(c, f"{n} cores", f.cx, f.top + 80, size=60, color=BLUE, weight="extrabold", alpha=f.p(0.0, 0.4))
    if w > 0:
        # all arrows point to the far RAM
        for i in range(n):
            x = f.cx - 300 + i * 85
            arrow(c, x, f.top + 460, f.cx, f.top + 760, color=RED, width=3, head=14, progress=w, alpha=0.5)
        box(c, f.cx, f.top + 840, 300, 150, fill="#1E1726", stroke=RAMC, width=5, radius=14, alpha=w)
        text(c, "RAM", f.cx, f.top + 840, size=50, color=RAMC, weight="extrabold", alpha=w)
    t = f.p("together", 0.4, "overshoot")
    if t > 0:
        with moved(c, scale=max(t, 0.001), about=(f.cx, f.top + 1040)):
            text(c, "everyone waits", f.cx, f.top + 1040, size=72, color=RED, weight="extrabold", glow=6)


# ------------------------------------------------------------------ 7. verdict
@VIDEO.scene("verdict", lines=[
    Line("In Watch Dogs Legion, six and eight cores tied. Cache added fifty-five percent.",
         show="In Watch Dogs: Legion, 6 and 8 cores tied. Cache added 55%."),
    Line("Those ninety-six megabyte chips? That's AMD's X three D.",
         show="Those 96 MB chips? That's AMD's X3D."),
], sfx=[("whoosh", 0.0), ("tick", "tied"), ("hit", "fifty-five"), ("pop", "three")], pad_out=0.4)
def verdict(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    text(c, "WATCH DOGS: LEGION", f.cx, f.top + 20, size=50, color=GREY, weight="extrabold", alpha=f.p(0.0, 0.5))
    base = f.top + 680
    k1 = f.p(("six", -0.1), 0.6, "out")
    bar(c, 240, base, 150, 300, color=BLUE, progress=k1, label="6 cores", value="100")
    bar(c, 430, base, 150, 300, color=BLUE, progress=f.p(("eight", -0.1), 0.6, "out"), label="8 cores",
        value="100")
    if f.after("tied"):
        text(c, "TIE", 335, base - 300 - 120, size=64, color=WHITE, weight="extrabold", alpha=f.p("tied", 0.3))
    k3 = f.p("fifty-five", 0.8, "overshoot")
    bar(c, 760, base, 180, 465, color=GOLD, progress=k3, label="96 MB cache", value="155")
    if k3 > 0:
        text(c, "+55%", 760, base - 465 - 120, size=72, color=GOLD, weight="extrabold", glow=8, alpha=clamp(k3 * 2))
    text(c, "relative FPS (16 MB = 100)", f.cx, base + 100, size=30, color=GREY, weight="medium", alpha=k1)
    x = f.p(("ninety-six", -0.1), 0.5, "overshoot")
    if x > 0:
        with moved(c, scale=max(x, 0.001), about=(f.cx, f.top + 950)):
            chip(c, f.cx - 300, f.top + 950, 170, color=PURPLE, label="X3D", label_color=WHITE, glow=0.7)
            text(c, "3D V-Cache", f.cx - 150, f.top + 920, size=56, color=PURPLE, weight="extrabold", align="left")
            text(c, "extra cache stacked on top", f.cx - 150, f.top + 985, size=34, color=GREY,
                 weight="medium", align="left")
