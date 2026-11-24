"""Short: 16 cores vs 8 cores, 1.4% apart (Gears of War: E-Day). Why: the game thread + Amdahl's law.

Lane: bridge (code told through the CPU in the viewer's PC). Series: "Spec says X, reality says Y".

Facts (see claude/cores-one-thread-short.md in the CC project):
- Tom's Hardware, "Gears of War: E-Day is an uncharacteristically CPU-heavy Unreal Engine 5 game"
  (Jake Roach, Oct 1, 2026): 25 CPUs, RTX 5090 FE, 1080p, High preset (table settings inferred from
  "same test scene and settings"). Stock averages: Ryzen 7 7700X (8 cores) 128.8 FPS, Ryzen 9 7950X
  (16 cores) 130.6 FPS (+1.4%), Ryzen 5 7600X 118.7, Ryzen 7 9800X3D (8 cores) 168.7 (fastest AMD
  chip in the table). Tom's: core count is a performance driver in this game, "which isn't usually
  the case in games past six or maybe eight cores".
- Unreal Engine docs (Threaded Rendering): "The game thread owns all AActor / UObject state";
  the renderer runs "in its own thread that is a frame or two behind the game thread."
- Amdahl's law (textbook): speedup = 1 / ((1 - p) + p / n). With p = 0.5 (illustrative):
  n=8 -> 1.78x, n=16 -> 1.88x, limit 2x.
Build: python -m studio.make videos/2026-11-24-cores-one-thread
"""
import math

from studio import *

VIDEO = Video("cores-one-thread", format="short", speed=1.10,
              question="How many cores does your CPU have?")

PANEL = "#161B23"


def cores(c, cx, cy, n, size=46, gap=10, cols=8, color=BLUE, alpha=1.0, busy=None, t=0.0):
    """n cores in rows of `cols`; `busy` = index of the one hot core (pulses gold)."""
    rows = math.ceil(n / cols)
    w = cols * size + (cols - 1) * gap
    h = rows * size + (rows - 1) * gap
    x0, y0 = cx - w / 2, cy - h / 2
    for i in range(n):
        r, k = divmod(i, cols)
        x, y = x0 + k * (size + gap), y0 + r * (size + gap)
        col = color
        a = alpha
        if busy is not None:
            if i == busy:
                col = GOLD
            else:
                a = alpha * 0.45
        rect(c, x, y, size, size, fill=col, radius=8, alpha=a)


def hbar(c, x, y, w, h, color, label, value, alpha=1.0):
    text(c, label, x, y - 34, size=38, color=GREY, weight="bold", align="left", alpha=alpha)
    rect(c, x, y, w, h, fill=color, radius=10, alpha=alpha)
    text(c, value, x + w - 20, y + h / 2, size=48, color=BG, weight="extrabold", align="right", alpha=alpha)


# ------------------------------------------------------------------ 1. hook
@VIDEO.scene("hook", lines=[
    Line("Sixteen cores. Eight cores. One point four percent apart.",
         show="16 cores. 8 cores. 1.4% apart."),
], pad_in=0.1, pad_out=0.9, sfx=[("whoosh", 0.0), ("pop", "sixteen"), ("pop", "eight"), ("hit", "one point four")])
def hook(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    a16 = f.p("sixteen", 0.5, "overshoot")
    a8 = f.p("eight", 0.5, "overshoot")
    y16, y8 = f.top + 120, f.top + 420
    if a16 > 0:
        with moved(c, scale=max(a16, 0.001), about=(f.cx, y16)):
            text(c, "16 CORES", f.cx, y16 - 90, size=58, color=BLUE, weight="extrabold")
            cores(c, f.cx, y16 + 20, 16, size=70, gap=14)
    if a8 > 0:
        with moved(c, scale=max(a8, 0.001), about=(f.cx, y8)):
            text(c, "8 CORES", f.cx, y8 - 60, size=58, color=BLUE, weight="extrabold")
            cores(c, f.cx, y8 + 30, 8, size=70, gap=14)
    k = f.p("one point four", 0.9, "out")
    if k > 0:
        yb = f.top + 640
        hbar(c, 110, yb, 30 + 830 * k, 80, BLUE, "16 cores", "130.6 FPS" if k > 0.7 else "", alpha=clamp(k * 3))
        hbar(c, 110, yb + 170, 30 + 818 * k, 80, GREY, "8 cores", "128.8 FPS" if k > 0.7 else "",
             alpha=clamp(k * 3))
        g = f.p(("one point four", 0.5), 0.5, "overshoot")
        if g > 0:
            with moved(c, scale=max(g, 0.001), about=(f.cx, f.top + 1060)):
                text(c, "+1.4%", f.cx, f.top + 1060, size=150, color=GOLD, weight="extrabold", glow=8)


# ------------------------------------------------------------------ 2. setup
@VIDEO.scene("setup", lines=[
    Line("Twenty-five CPUs. Gears of War E Day. One R T X fifty-ninety.",
         show="25 CPUs. Gears of War: E-Day. One RTX 5090."),
    Line("Twice the cores. Why not twice the speed?"),
], sfx=[("tick", "twenty-five"), ("tick", "gears"), ("tick", "fifty-ninety"), ("swell", "why")])
def setup(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    items = [("twenty-five", "25 CPUs", "Intel and AMD", BLUE),
             ("gears", "Gears of War: E-Day", "a game that does use many cores", GREEN),
             ("fifty-ninety", "RTX 5090 · 1080p", "same GPU for all", GOLD)]
    for i, (cue, big, small, col) in enumerate(items):
        k = f.p(cue, 0.5, "out")
        y = f.top + 40 + i * 190
        with moved(c, dx=(1 - k) * 140, alpha=k):
            rect(c, 110, y, 860, 160, fill=PANEL, stroke=col, width=4, radius=20)
            text(c, big, 160, y + 60, size=50, color=col, weight="extrabold", align="left")
            text(c, small, 160, y + 118, size=34, color=GREY, weight="medium", align="left")
    text(c, "Source: Tom's Hardware, Oct 1, 2026", f.cx, f.top + 640, size=30, color=GREY,
         weight="medium", alpha=f.p("fifty-ninety", 0.5))
    d = f.p("twice", 0.5, "out")
    if d > 0:
        runs(c, [("2× cores", BLUE), ("  →  ", GREY), ("2× FPS?", GOLD)], f.cx, f.top + 800, size=70,
             weight="extrabold", alpha=d)
    q = f.p("why", 0.5, "overshoot")
    if q > 0:
        with moved(c, scale=max(q, 0.001), about=(f.cx, f.top + 990)):
            text(c, "WHY NOT?", f.cx, f.top + 990, size=120, color=WHITE, weight="extrabold")


# ------------------------------------------------------------------ 3-4. one frame as lanes
LX, LW = 250, 760          # lane area: x from LX, width LW (= one frame, 1/130 s)
LANE_H, LANE_GAP = 62, 20


@VIDEO.scene("frame", lines=[
    Line("Each frame, one thread runs the game itself: input, AI, physics."),
    Line("Unreal even names it: the game thread."),
    Line("Other cores take the side jobs."),
], sfx=[("whoosh", 0.0), ("pop", "one thread"), ("ding", "game thread"), ("pop", "other")])
def frame(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    a = f.p(0.0, 0.5)
    y0 = f.top + 120
    game_w = LW * 0.5
    text(c, "one frame", LX + LW / 2, y0 - 50, size=34, color=GREY, weight="bold", alpha=a)
    line(c, LX, y0 - 20, LX + LW, y0 - 20, color=GREY, width=2, alpha=a * 0.6)
    g = f.p("one thread", 0.8, "out")
    rect(c, LX, y0, LW, LANE_H, fill=PANEL, radius=8, alpha=a)
    text(c, "game", LX - 20, y0 + LANE_H / 2, size=30, color=GOLD, weight="bold", align="right", alpha=a)
    if g > 0:
        rect(c, LX, y0, game_w * g, LANE_H, fill=GOLD, radius=8)
    for j, (cue, lab) in enumerate([("input", "input"), ("ai", "AI"), ("physics", "physics")]):
        k = f.p(cue, 0.35, "overshoot")
        if k > 0:
            x = LX + 70 + j * 125
            with moved(c, scale=max(k, 0.001), about=(x, y0 + LANE_H / 2)):
                text(c, lab, x, y0 + LANE_H / 2, size=28, color=BG, weight="extrabold")
    n = f.p("names", 0.5, "overshoot")
    if n > 0:
        with moved(c, scale=max(n, 0.001), about=(f.cx, f.top + 340)):
            box(c, f.cx, f.top + 340, 640, 120, fill=PANEL, stroke=GOLD, width=4, radius=60)
            text(c, "the game thread", f.cx, f.top + 340, size=58, color=GOLD, weight="extrabold")
        text(c, "\"owns all\" the game's objects: Unreal Engine docs", f.cx, f.top + 450, size=28,
             color=GREY, weight="medium", alpha=f.p(("names", 0.4), 0.5))
    o = f.p("other", 0.6, "out")
    if o > 0:
        yw = f.top + 560
        for i in range(4):
            y = yw + i * (LANE_H + LANE_GAP)
            k = clamp(o * 1.6 - i * 0.2)
            text(c, f"core {i + 2}", LX - 20, y + LANE_H / 2, size=30, color=GREY, weight="bold",
                 align="right", alpha=k)
            rect(c, LX, y, LW, LANE_H, fill=PANEL, radius=8, alpha=k)
            rect(c, LX + 40, y, (LW * 0.42) * k, LANE_H, fill=BLUE, radius=8, alpha=k * 0.9)
        labels = ["sound", "streaming", "particles", "loading"]
        for i, lab in enumerate(labels):
            y = yw + i * (LANE_H + LANE_GAP)
            text(c, lab, LX + 60, y + LANE_H / 2, size=28, color=BG, weight="bold", align="left",
                 alpha=f.p(("jobs", 0.1 * i), 0.4))


@VIDEO.scene("more", lines=[
    Line("Add more cores, and the side jobs shrink."),
    Line("The game thread doesn't. The frame waits for it."),
], sfx=[("pop", "more"), ("whoosh", "shrink"), ("hit", "doesn't")])
def more(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    y0 = f.top + 60
    game_w = LW * 0.5
    k = f.p("more", 1.2, "smooth")
    n = int(round(lerp(4, 12, k)))
    side = LW * 0.42 * 4 / n                  # side work split over n workers
    lane_h = lerp(LANE_H, 40, k)
    gap = lerp(LANE_GAP, 10, k)
    text(c, f"{n + 1} cores", f.cx, y0 - 10, size=50, color=BLUE, weight="extrabold")
    yy = y0 + 50
    rect(c, LX, yy, LW, lane_h, fill=PANEL, radius=8)
    hot = f.after("doesn't")
    ga = 0.75 + 0.25 * pulse(f.t * 2.5) if hot else 1.0
    rect(c, LX, yy, game_w, lane_h, fill=GOLD, radius=8, alpha=ga)
    text(c, "game", LX - 20, yy + lane_h / 2, size=28, color=GOLD, weight="bold", align="right")
    for i in range(n):
        y = yy + (i + 1) * (lane_h + gap)
        rect(c, LX, y, LW, lane_h, fill=PANEL, radius=6)
        rect(c, LX + 40, y, side, lane_h, fill=BLUE, radius=6, alpha=0.9)
    bottom = yy + (n + 1) * (lane_h + gap)
    # frame end marker: set by the game thread
    s = f.p("doesn't", 0.5)
    if s > 0:
        x = LX + game_w
        line(c, x, yy - 20, x, bottom, color=RED, width=5, progress=s)
        text(c, "frame done", x, bottom + 40, size=38, color=RED, weight="extrabold", alpha=s)
    w = f.p("waits", 0.5, "overshoot")
    if w > 0:
        with moved(c, scale=max(w, 0.001), about=(f.cx, f.top + 1060)):
            text(c, "the frame waits for ONE core", f.cx, f.top + 1060, size=58, color=WHITE,
                 weight="extrabold", glow=4)


# ------------------------------------------------------------------ 5. Amdahl's law
@VIDEO.scene("amdahl", lines=[
    Line("Say half of each frame is stuck on that thread."),
    Line("Eight cores: one point eight times faster. Sixteen: one point nine. Never past two.",
         show="8 cores: 1.8x faster. 16: 1.9x. Never past 2x."),
    Line("That's Amdahl's law."),
], sfx=[("tick", "half"), ("pop", "eight"), ("pop", "sixteen"), ("hit", "never"), ("ding", "law")])
def amdahl(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    # axes: cores 1..16 on x, speedup 1..2.2 on y
    X0, X1 = 170, 960
    Y0, Y1 = f.top + 820, f.top + 260         # y for speedup 0 and 2.2 (we start at 0)
    a = f.p(0.0, 0.5)

    def px(n):
        return X0 + (n - 1) / 15 * (X1 - X0)

    def py(s):
        return Y0 - s / 2.2 * (Y0 - Y1)

    line(c, X0, Y0, X1 + 20, Y0, color=GREY, width=3, alpha=a)
    line(c, X0, Y0, X0, Y1 - 20, color=GREY, width=3, alpha=a)
    for n in (1, 4, 8, 12, 16):
        text(c, str(n), px(n), Y0 + 36, size=30, color=GREY, weight="bold", alpha=a)
    text(c, "cores", (X0 + X1) / 2, Y0 + 86, size=34, color=GREY, weight="bold", alpha=a)
    for s in (1, 2):
        text(c, f"{s}×", X0 - 24, py(s), size=32, color=GREY, weight="bold", align="right", alpha=a)
    # half-frame bar at top: gold half locked, blue half splittable
    h = f.p("half", 0.6, "out")
    if h > 0:
        yb = f.top + 70
        rect(c, 110, yb, 430, 80, fill=GOLD, radius=10, alpha=h)
        rect(c, 540, yb, 430 * h, 80, fill=BLUE, radius=10, alpha=h)
        text(c, "1 thread only", 325, yb + 40, size=36, color=BG, weight="extrabold", alpha=h)
        text(c, "splits across cores", 755, yb + 40, size=34, color=BG, weight="extrabold", alpha=h)
    # limit line at 2x
    lim = f.p("never", 0.6)
    if lim > 0:
        line(c, X0, py(2), X1, py(2), color=RED, width=4, progress=lim)
        text(c, "limit: 2×", X1, py(2) - 34, size=36, color=RED, weight="extrabold", align="right", alpha=lim)
    # the curve writes on from "eight"
    cp = f.p(("eight", -0.4), 2.2, "smooth")
    if cp > 0:
        pts = [(px(n), py(1 / (0.5 + 0.5 / n))) for n in [1 + 15 * i / 80 for i in range(81)]]
        stroke_path(c, polyline(pts), color=GOLD, width=7, progress=cp)
    for cue, n, lab in (("eight", 8, "1.78×"), ("sixteen", 16, "1.88×")):
        k = f.p(cue, 0.4, "overshoot")
        if k > 0:
            s = 1 / (0.5 + 0.5 / n)
            circle(c, px(n), py(s), 14 * min(k, 1.2), fill=GOLD)
            text(c, lab, px(n) - (0 if n == 8 else 30), py(s) + 56, size=44, color=GOLD, weight="extrabold",
                 alpha=clamp(k))
    l = f.p("law", 0.5, "overshoot")
    if l > 0:
        with moved(c, scale=max(l, 0.001), about=(f.cx, f.top + 1040)):
            runs(c, [("speedup = ", WHITE), ("1 ÷ (serial + parallel ÷ cores)", BLUE)], f.cx, f.top + 1000,
                 size=40, weight="bold")
            text(c, "Amdahl's law", f.cx, f.top + 1080, size=64, color=GOLD, weight="extrabold")
    text(c, "illustration: half the frame on one thread", f.cx, f.top + 180, size=28, color=GREY,
         weight="medium", alpha=h)


# ------------------------------------------------------------------ 6. verdict
@VIDEO.scene("verdict", lines=[
    Line("The eight-core ninety-eight hundred X three D? One sixty-nine. It beats both.",
         show="The 8-core 9800X3D? 169. It beats both."),
    Line("For games, faster cores beat more cores."),
], sfx=[("whoosh", 0.0), ("riser", ("eight-core", -0.4)), ("hit", "sixty-nine"), ("ding", "beat")], pad_out=0.4)
def verdict(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    text(c, "GEARS OF WAR: E-DAY · avg FPS", f.cx, f.top + 20, size=42, color=GREY, weight="extrabold",
         alpha=f.p(0.0, 0.5))
    base = f.top + 760
    scale = 3.6
    data = [("7700X", "8 cores", 128.8, GREY, (0.2)),
            ("7950X", "16 cores", 130.6, BLUE, (0.5)),
            ("9800X3D", "8 cores", 168.7, GOLD, ("sixty-nine", -0.5))]
    for i, (name, sub, v, col, cue) in enumerate(data):
        x = 230 + i * 310
        k = f.p(cue, 0.7, "out")
        h = (v - 60) * scale * k
        if k > 0:
            rect(c, x - 95, base - h, 190, h, fill=col, radius=12)
            text(c, f"{v:.1f}", x, base - h - 46, size=50, color=col, weight="extrabold", alpha=clamp(k * 2))
        text(c, name, x, base + 46, size=40, color=WHITE, weight="extrabold", alpha=f.p(cue, 0.4))
        text(c, sub, x, base + 96, size=32, color=col if col != GREY else GREY, weight="bold",
             alpha=f.p(cue, 0.4))
    text(c, "axis starts at 60 FPS · Tom's Hardware, 1080p", f.cx, base + 160, size=26, color=GREY,
         weight="medium", alpha=f.p((0.5), 0.5))
    b = f.p("beat", 0.5, "overshoot")
    if b > 0:
        with moved(c, scale=max(b, 0.001), about=(f.cx, f.top + 1060)):
            runs(c, [("faster cores", GOLD), (" > ", WHITE), ("more cores", BLUE)], f.cx, f.top + 1060,
                 size=72, weight="extrabold")
