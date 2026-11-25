"""Short: GTA 6 is 30 FPS even on PS5 Pro. The GPU got up to 45% faster; the CPU ~10%.

Lane: proven (hardware: the CPU and GPU in the viewer's console / PC). Series: "Spec says X, reality says Y".

Facts (see claude/gta6-cpu-30fps-short.md in the CC project):
- GTA VI launched Nov 19, 2026 (Fox10, Oct 16, 2026; tbreak, Nov 20, 2026).
- Rockstar (Marc Chambers, Technology Production Director, statement to Kotaku, relayed Nov 18-20, 2026):
  the PS5 Pro's CPU is "slightly better" than the base PS5's but "not powerful enough to run the game's
  complex simulation at higher frame rates." 30 FPS target on PS5, PS5 Pro, Series X and Series S.
  (sixshore Nov 18, tbreak Nov 20, Club386 Nov 19, 2026)
- Digital Foundry (via sixshore / tbreak): PS5 Pro "near-flawless 30", worst stress-test dip 24 FPS;
  base PS5 23 FPS in the same explosion scene. PS5 Pro adds ray-traced shadows and PSSR upscaling.
- Sony (PS5 Pro reveal, Sep 10, 2024): GPU renders "up to 45% faster" than PS5. CPU: 8 Zen 2 cores,
  up to 3.85 GHz (PS5: up to 3.5 GHz) -> +10%. Zen 2 first shipped in July 2019 (Ryzen 3000).
- Frame budget: 1000/30 = 33.3 ms; 1000/60 = 16.7 ms.
Build: python -m studio.make videos/2026-11-25-gta6-cpu-30fps
"""
import math
import random

from studio import *

VIDEO = Video("gta6-cpu-30fps", format="short", speed=1.15,
              question="Would you play GTA 6 at 30 FPS?")
VIDEO.endcard_lines = [
    Line("Would you play GTA six at thirty F P S? Tell me in the comments.",
         show="Would you play GTA 6 at 30 FPS? Tell me in the comments."),
    Line("And if this helped, like, share, and subscribe to The Thinking Sand.",
         show="If this helped: like, share, and subscribe to The Thinking Sand."),
]

PANEL = "#161B23"


def hbar(c, x, y, w, h, color, label, value, alpha=1.0, vcolor=BG):
    text(c, label, x, y - 34, size=38, color=GREY, weight="bold", align="left", alpha=alpha)
    rect(c, x, y, w, h, fill=color, radius=10, alpha=alpha)
    if value:
        text(c, value, x + w - 20, y + h / 2, size=46, color=vcolor, weight="extrabold", align="right",
             alpha=alpha)


def city(c, x, y, w, h, t, n=46, alpha=1.0, seed=7):
    """A tiny top-down city: a road grid with cars (gold) and people (blue) moving along it."""
    rect(c, x, y, w, h, fill=PANEL, radius=18, alpha=alpha)
    cols, rows = 5, 4
    for i in range(1, cols):
        xx = x + w * i / cols
        line(c, xx, y + 14, xx, y + h - 14, color=DIM, width=10, alpha=alpha)
    for j in range(1, rows):
        yy = y + h * j / rows
        line(c, x + 14, yy, x + w - 14, yy, color=DIM, width=10, alpha=alpha)
    for k in range(n):
        rng = random.Random(seed * 1000 + k)
        r, s = rng.random(), rng.random()
        car = k % 3 == 0
        speed = 0.09 if car else 0.03
        u = (r + t * speed * (1 if k % 2 else -1)) % 1.0
        if k % 2:      # along a horizontal road
            j = 1 + int(s * (rows - 1)) % (rows - 1)
            px, py = x + 20 + u * (w - 40), y + h * j / rows
        else:          # along a vertical road
            i = 1 + int(s * (cols - 1)) % (cols - 1)
            px, py = x + w * i / cols, y + 20 + u * (h - 40)
        if car:
            rect(c, px - 9, py - 6, 18, 12, fill=GOLD, radius=3, alpha=alpha)
        else:
            circle(c, px + (6 if k % 4 == 1 else -6), py + (6 if k % 4 == 3 else -6), 4.5, fill=BLUE,
                   alpha=alpha)


# ------------------------------------------------------------------ 1. hook
@VIDEO.scene("hook", lines=[
    Line("The P S five Pro's GPU is up to forty-five percent faster.",
         show="The PS5 Pro's GPU: up to 45% faster."),
    Line("GTA six still runs at thirty F P S.", show="GTA 6 still runs at 30 FPS."),
], pad_in=0.1, pad_out=0.3, sfx=[("whoosh", 0.0), ("pop", "pro's"), ("riser", ("forty-five", -0.6)),
                                 ("hit", "thirty")])
def hook(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    a = f.p(0.05, 0.5, "out")
    text(c, "GPU POWER", f.cx, f.top + 40, size=46, color=GREY, weight="extrabold", alpha=a)
    k = f.p(("pro's", 0.1), 1.4, "out")
    W0 = 560
    hbar(c, 110, f.top + 160, W0, 90, GREY, "PS5", "100%", alpha=a)
    hbar(c, 110, f.top + 340, max(W0 * (1 + 0.45 * k), 1), 90, BLUE, "PS5 Pro",
         f"{100 + 45 * k:.0f}%", alpha=clamp(k * 4))
    g = f.p("forty-five", 0.5, "overshoot")
    if g > 0:
        with moved(c, scale=max(g, 0.001), about=(f.cx, f.top + 560)):
            text(c, "up to +45%", f.cx, f.top + 560, size=64, color=BLUE, weight="extrabold")
        text(c, "Sony's claim", f.cx, f.top + 625, size=28, color=GREY, weight="medium", alpha=clamp(g))
    s = f.p("gta", 0.5, "out")
    if s > 0:
        text(c, "GTA 6 frame rate", f.cx, f.top + 760, size=46, color=WHITE, weight="extrabold", alpha=s)
    h = f.p("thirty", 0.45, "overshoot")
    if h > 0:
        with moved(c, scale=max(h, 0.001), about=(f.cx, f.top + 940)):
            text(c, "30 FPS", f.cx, f.top + 940, size=200, color=GOLD, weight="extrabold", glow=10)
        text(c, "same as the base PS5", f.cx, f.top + 1080, size=36, color=GREY, weight="bold",
             alpha=f.p(("thirty", 0.4), 0.5))


# ------------------------------------------------------------------ 2. Rockstar's answer
QUOTE = "“not powerful enough to run the game's complex simulation at higher frame rates”"


@VIDEO.scene("quote", lines=[
    Line("Rockstar says the Pro's processor is not powerful enough",
         show="Rockstar: the Pro's CPU is \"not powerful enough"),
    Line("to run the game's complex simulation at higher frame rates.",
         show="to run the game's complex simulation at higher frame rates.\""),
], sfx=[("whoosh", 0.0), ("tick", "processor"), ("ding", "simulation")])
def quote(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    a = f.p(0.0, 0.5, "out")
    text(c, "ROCKSTAR, ON THE PS5 PRO", f.cx, f.top + 60, size=40, color=GREY, weight="extrabold", alpha=a)
    k = f.p("processor", 0.6, "overshoot")
    if k > 0:
        with moved(c, scale=max(k, 0.001), about=(f.cx, f.top + 300)):
            chip(c, f.cx, f.top + 300, 230, color=RED, label="CPU", glow=4 * pulse(f.t * 1.5))
    q = f.p(("not", 0.0), f.line_end(1) - f.cue("not") - 0.3, "linear")
    if q > 0:
        box(c, f.cx, f.top + 700, 900, 340, fill=PANEL, stroke=GOLD, width=3, radius=24, alpha=clamp(q * 5))
        text(c, typewriter(QUOTE, q), f.cx, f.top + 700, size=50, color=WHITE, weight="bold",
             max_width=800)
    s = f.p(("simulation", 0.2), 0.5)
    text(c, "Marc Chambers, Rockstar, to Kotaku · Nov 2026", f.cx, f.top + 930, size=28, color=GREY,
         weight="medium", alpha=s)


# ------------------------------------------------------------------ 3. what the CPU does per frame
BX, BW = 110, 860      # frame-budget ruler: x from BX, width BW = 33.3 ms


@VIDEO.scene("budget", lines=[
    Line("Every frame, the CPU moves the whole city first.",
         show="Every frame, the CPU moves the whole city first."),
    Line("At thirty F P S, that's thirty-three milliseconds.", show="At 30 FPS, that's 33 milliseconds."),
    Line("Sixty leaves sixteen point seven. It doesn't fit.",
         show="60 leaves 16.7. It doesn't fit."),
], sfx=[("whoosh", 0.0), ("pop", "whole"), ("pop", "city"), ("tick", "thirty-three"),
        ("hit", "fit")])
def budget(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    a = f.p(0.0, 0.6, "out")
    city(c, 110, f.top + 30, 860, 470, f.T, alpha=a)
    for cue, lab, col, x in (("whole", "cars", GOLD, 330), ("city", "people", BLUE, 760)):
        k = f.p(cue, 0.4, "overshoot")
        if k > 0:
            with moved(c, scale=max(k, 0.001), about=(x, f.top + 560)):
                box(c, x, f.top + 560, 250, 70, fill=PANEL, stroke=col, width=3, radius=35)
                text(c, lab, x, f.top + 560, size=40, color=col, weight="extrabold")
    # the ruler: one frame at 30 FPS
    r = f.p("thirty", 0.6, "out")
    y = f.top + 760
    if r > 0:
        line(c, BX, y - 50, BX + BW * r, y - 50, color=GREY, width=3)
        text(c, "one frame at 30 FPS = 33.3 ms", f.cx, y - 90, size=36, color=WHITE, weight="bold", alpha=r)
        rect(c, BX, y, BW, 110, fill=PANEL, radius=12, alpha=r)
        cpu_w = BW * 0.78 * f.p(("thirty", 0.3), 1.2, "out")
        late = f.after("fit")
        if cpu_w > 1:
            rect(c, BX, y, cpu_w, 110, fill=RED if late else GOLD, radius=12)
            text(c, "CPU: simulate the city", BX + 24, y + 55, size=38, color=BG, weight="extrabold",
                 align="left", alpha=clamp(cpu_w / 400))
    s = f.p("sixty", 0.6)
    if s > 0:
        x = BX + BW / 2
        line(c, x, y - 30, x, y + 150, color=BLUE, width=6, progress=s)
        text(c, "60 FPS: 16.7 ms", x, y + 195, size=40, color=BLUE, weight="extrabold", alpha=s)
    d = f.p("fit", 0.5, "overshoot")
    if d > 0:
        with moved(c, scale=max(d, 0.001), about=(f.cx, f.top + 1035)):
            text(c, "doesn't fit", f.cx, f.top + 1035, size=90, color=RED, weight="extrabold", glow=6)
    text(c, "illustration, not a measured frame", f.cx, f.top + 1125, size=26, color=GREY, weight="medium",
         alpha=r * 0.9)


# ------------------------------------------------------------------ 4. the CPU barely changed
@VIDEO.scene("cpu", lines=[
    Line("And the Pro kept the same eight Zen two cores from twenty nineteen,",
         show="And the Pro kept the same 8 Zen 2 cores from 2019,"),
    Line("clocked only about ten percent higher.", show="clocked only about 10% higher."),
], sfx=[("whoosh", 0.0), ("pop", "eight"), ("tick", "nineteen"), ("hit", "ten")], pad_out=0.35)
def cpu(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    k = f.p("eight", 0.8, "out")
    size, gap = 96, 16
    w = 4 * size + 3 * gap
    x0 = f.cx - w / 2
    y0 = f.top + 70
    blocks(c, x0, y0, 8, 8, cols=4, size=size, gap=gap, on=BLUE, progress=k, alpha=max(k, 0.25))
    z = f.p("zen", 0.5, "out")
    text(c, "8 × Zen 2", f.cx, y0 + 2 * size + gap + 70, size=60, color=BLUE, weight="extrabold", alpha=z)
    n = f.p("nineteen", 0.5, "overshoot")
    if n > 0:
        with moved(c, scale=max(n, 0.001), about=(f.cx, y0 + 2 * size + gap + 150)):
            text(c, "first shipped in 2019", f.cx, y0 + 2 * size + gap + 150, size=40, color=GREY,
                 weight="bold")
    # clocks
    g = f.p("clocked", 0.5, "out")
    yb = f.top + 560
    if g > 0:
        hbar(c, 110, yb, 700, 80, GREY, "PS5 CPU", "3.5 GHz", alpha=g)
        kk = f.p(("only", 0.0), 0.8, "out")
        hbar(c, 110, yb + 160, 700 * (1 + 0.1 * kk), 80, BLUE, "PS5 Pro CPU",
             "3.85 GHz" if kk > 0.5 else "", alpha=clamp(kk * 3))
    t = f.p("ten", 0.5, "overshoot")
    if t > 0:
        with moved(c, scale=max(t, 0.001), about=(f.cx, f.top + 960)):
            runs(c, [("CPU ", WHITE), ("+10%", RED), ("   GPU ", WHITE), ("+45%", BLUE)], f.cx,
                 f.top + 960, size=72, weight="extrabold")
    text(c, "Sony's specs: \"up to\" clocks", f.cx, f.top + 1060, size=28, color=GREY, weight="medium",
         alpha=f.p(("ten", 0.3), 0.5))


# ------------------------------------------------------------------ 5. the faster GPU waits
LX, LW = 230, 760


@VIDEO.scene("waits", lines=[
    Line("The GPU can't draw a frame the CPU hasn't finished, so a faster one just waits.",
         show="The GPU can't draw a frame the CPU hasn't finished, so a faster one just waits."),
    Line("The Pro spends it on prettier frames instead.",
         show="The Pro spends it on prettier frames instead."),
], sfx=[("whoosh", 0.0), ("pop", "waits"), ("ding", "prettier"), ("ding", "frames")])
def waits(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    a = f.p(0.0, 0.5, "out")
    y0 = f.top + 80
    fw = LW / 3                      # three frames side by side
    text(c, "3 frames", LX + LW / 2, y0 - 40, size=34, color=GREY, weight="bold", alpha=a)
    # lane backgrounds
    for i, (lab, col) in enumerate((("CPU", GOLD), ("GPU", BLUE))):
        y = y0 + i * 130
        text(c, lab, LX - 24, y + 45, size=40, color=col, weight="extrabold", align="right", alpha=a)
        rect(c, LX, y, LW, 90, fill=PANEL, radius=10, alpha=a)
    run = f.p(0.2, 2.2, "linear")
    for j in range(3):
        x = LX + j * fw
        k = clamp(run * 3 - j)
        if k > 0:
            rect(c, x + 4, y0, (fw - 8) * k, 90, fill=GOLD, radius=10)
        # GPU draws frame j while the CPU works on j+1; it is short, then idles
        g = clamp(run * 3 - j - 1)
        gpu_len = (fw - 8) * lerp(0.62, 0.40, f.p("faster", 0.8))
        if g > 0 and j < 2:
            gx = x + fw + 4
            rect(c, gx, y0 + 130, gpu_len * g, 90, fill=BLUE, radius=10)
            if f.after("waits") and g >= 1:
                ww = fw - 8 - gpu_len
                rect(c, gx + gpu_len, y0 + 130, ww, 90, stroke=GREY, width=3, radius=10,
                     alpha=0.5 + 0.3 * pulse(f.t * 2))
                text(c, "idle", gx + gpu_len + ww / 2, y0 + 175, size=30, color=GREY, weight="bold")
    # looks
    items = [("prettier", "sharper upscaling", "PSSR, close to 4K"), (("frames", 0.1), "ray-traced shadows",
                                                                     "Pro only")]
    for i, (cue, big, small) in enumerate(items):
        k = f.p(cue, 0.5, "out")
        if k > 0:
            y = f.top + 520 + i * 220
            with moved(c, dx=(1 - k) * 140, alpha=k):
                rect(c, 110, y, 860, 170, fill=PANEL, stroke=BLUE, width=4, radius=20)
                text(c, big, 160, y + 65, size=54, color=BLUE, weight="extrabold", align="left")
                text(c, small, 160, y + 125, size=32, color=GREY, weight="medium", align="left")
    text(c, "Digital Foundry, via sixshore / tbreak, Nov 2026", f.cx, f.top + 1000, size=26, color=GREY,
         weight="medium", alpha=f.p("prettier", 0.5))


# ------------------------------------------------------------------ 6. verdict
@VIDEO.scene("verdict", lines=[
    Line("Digital Foundry: a near-flawless thirty, dipping to twenty-four.",
         show="Digital Foundry: a near-flawless 30, dipping to 24."),
    Line("Your frame rate is set by the slowest chip.",
         show="Your frame rate is set by the slowest chip."),
], sfx=[("whoosh", 0.0), ("tick", "thirty"), ("hit", "twenty-four"), ("riser", ("slowest", -0.6)),
        ("ding", ("chip", 0.3))], pad_out=0.7)
def verdict(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    X0, X1 = 150, 970
    Y30, Y20 = f.top + 220, f.top + 520            # y for 30 FPS and 20 FPS
    a = f.p(0.0, 0.5)

    def py(v):
        return Y20 + (v - 20) / 10 * (Y30 - Y20)

    text(c, "PS5 Pro · GTA 6 · FPS", f.cx, f.top + 40, size=42, color=GREY, weight="extrabold", alpha=a)
    for v in (20, 30):
        line(c, X0, py(v), X1, py(v), color=DIM, width=2, alpha=a)
        text(c, str(v), X0 - 20, py(v), size=32, color=GREY, weight="bold", align="right", alpha=a)
    # a flat 30 line with one dip to 24 (shape illustrative; the 30 and 24 are DF's)
    pts = []
    for i in range(121):
        u = i / 120
        v = 30 - 6 * math.exp(-((u - 0.68) / 0.035) ** 2)
        pts.append((X0 + u * (X1 - X0), py(v)))
    s = f.p(("near-flawless", -0.3), 1.8, "smooth")
    if s > 0:
        stroke_path(c, polyline(pts), color=GOLD, width=7, progress=s)
    d = f.p("twenty-four", 0.5, "overshoot")
    if d > 0:
        x = X0 + 0.68 * (X1 - X0)
        circle(c, x, py(24), 14 * min(d, 1.2), fill=RED)
        text(c, "24", x, py(24) + 60, size=56, color=RED, weight="extrabold", alpha=clamp(d))
        text(c, "explosion stress test", x, py(24) + 115, size=28, color=GREY, weight="medium", alpha=clamp(d))
    b = f.p("slowest", 0.6, "out")
    if b > 0:
        y = f.top + 820
        with moved(c, alpha=b):
            chip(c, 330, y, 190, color=RED, label="CPU")
            chip(c, 750, y, 190, color=BLUE, label="GPU")
            text(c, "slowest", 330, y + 180, size=44, color=RED, weight="extrabold")
            text(c, "strongest", 750, y + 180, size=44, color=BLUE, weight="extrabold",
                 alpha=f.p(("slowest", 0.3), 0.4))
    w = f.p(("chip", 0.2), 0.5, "overshoot")
    if w > 0:
        with moved(c, scale=max(w, 0.001), about=(330, f.top + 820)):
            circle(c, 330, f.top + 820, 138, stroke=GOLD, width=8)
        text(c, "sets your FPS", 330, f.top + 1075, size=48, color=GOLD, weight="extrabold", alpha=clamp(w))
