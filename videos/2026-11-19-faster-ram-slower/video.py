"""Short: faster RAM made the game slower (DDR5-8000 vs DDR5-6000 on Ryzen).

Lane: proven (hardware). Series: "Spec says X, reality says Y".

Facts (see claude/faster-ram-slower-short.md in the CC project):
- TheFPSReview, "G.SKILL Trident Z5 Neo RGB DDR5 8000MT/s EXPO Memory Review - Is DDR5-8000
  Worth It on AMD Ryzen?" (Aug 6, 2026), Ryzen 9 9950X, 1080p CPU-bound settings:
  Horizon Forbidden West: DDR5-6000 CL28 +24% over DDR5-4800; "at the EXPO 8000MT/s it lagged
  behind DDR5-6000 by 8%". DDR5-6000 CL28 beat 8000 in most games tested.
  "the memory controller frequency gets cut in half, and ends up actually running slower
  (2000MHz)" vs "DDR5-6000 (3000MHz)". Advice: "get the lowest-latency DDR5-6000 you can, if
  gaming is your goal."
- 8000 / 6000 = 1.33 -> "33% faster" (data rate on the box).
- DDR5-6000: memory clock 3000 MHz (two transfers per clock); DDR5-8000: 4000 MHz.
- TechPowerUp "AMD 3D V-Cache memory performance scaling" (via TweakTown, Sep 22, 2026):
  Ryzen 7 9800X3D, RTX 4090, 1080p, 8 games: about 2% between the slowest kit (DDR5-4800 JEDEC)
  and the fastest (DDR5-6000 CL30).
Build: python -m studio.make videos/2026-11-19-faster-ram-slower
"""
import math
import random

import skia

from studio import *

VIDEO = Video("faster-ram-slower", format="short", speed=1.08,
              question="What speed is your RAM running at?")

PCB = "#1F6B4F"
PCB_EDGE = "#2E8F6A"
MEMCHIP = "#151A21"


# ------------------------------------------------------------------ helpers
def ram_stick(c, cx, cy, w, label, color=GOLD, alpha=1.0, glow=0.0, chips=8):
    """A horizontal DDR5 module centred on (cx, cy), width w."""
    h = w * 0.24
    x, y = cx - w / 2, cy - h / 2
    if glow > 0:
        rect(c, x, y, w, h, fill=color, radius=10, alpha=alpha * 0.45 * glow, blur=30)
    rect(c, x, y, w, h, fill=PCB, stroke=PCB_EDGE, width=3, radius=10, alpha=alpha)
    # gold contacts
    n = 40
    for i in range(n):
        if i == n // 2 - 3:
            continue  # the key notch
        rect(c, x + 14 + i * (w - 28) / n, y + h - 18, (w - 28) / n * 0.6, 14, fill="#D9B44A",
             radius=2, alpha=alpha)
    # memory chips
    cw = (w - 60) / chips
    for i in range(chips):
        rect(c, x + 30 + i * cw + 4, y + 16, cw - 8, h * 0.5, fill=MEMCHIP, radius=4, alpha=alpha)
    # label sticker
    if label:
        lw = w * 0.56
        box(c, cx, y + 16 + h * 0.25, lw, h * 0.34, fill=color, radius=8, alpha=alpha)
        text(c, label, cx, y + 16 + h * 0.25, size=h * 0.2, color=BG, weight="extrabold", alpha=alpha)


def dial(c, cx, cy, r, angle, color, label, mhz, alpha=1.0, glow=0.0):
    """A clock dial with a spinning hand: the 'tick' of a clock domain."""
    if glow > 0:
        circle(c, cx, cy, r, fill=color, alpha=alpha * 0.25 * glow, blur=30)
    circle(c, cx, cy, r, fill="#141920", stroke=color, width=6, alpha=alpha)
    for i in range(12):
        a = i / 12 * 2 * math.pi
        line(c, cx + (r - 22) * math.cos(a), cy + (r - 22) * math.sin(a),
             cx + (r - 8) * math.cos(a), cy + (r - 8) * math.sin(a), color=GREY, width=3, alpha=alpha)
    a = angle - math.pi / 2
    line(c, cx, cy, cx + (r - 30) * math.cos(a), cy + (r - 30) * math.sin(a), color=color, width=8,
         alpha=alpha)
    circle(c, cx, cy, 10, fill=WHITE, alpha=alpha)
    text(c, label, cx, cy - r - 44, size=38, color=GREY, weight="bold", alpha=alpha)
    text(c, mhz, cx, cy + r + 56, size=54, color=color, weight="extrabold", alpha=alpha)


def packets(c, x, y0, y1, t, rate, color, alpha=1.0, phase=0.0, size=16):
    """Data packets travelling from y0 to y1 at `rate` packets per second."""
    if alpha <= 0:
        return
    span = y1 - y0
    speed = 1.6  # trips per second (fraction of the path)
    n = int(rate * 2) + 2
    for i in range(n):
        u = ((t + phase) * speed + i / max(rate, 0.1) * speed) % 1.0
        if i / max(rate, 0.1) * speed > 1.0 + speed * 1.0:
            break
        py = y0 + span * u
        a = alpha * min(1, u * 6, (1 - u) * 6)
        box(c, x, py, size * 1.6, size, fill=color, radius=4, alpha=a)


# ------------------------------------------------------------------ 1. hook
@VIDEO.scene("hook", lines=[
    Line("This RAM is thirty-three percent faster on the box.",
         show="This RAM is 33% faster on the box."),
    Line("In Horizon Forbidden West, it was eight percent slower.",
         show="In Horizon Forbidden West, it was 8% slower."),
], pad_in=0.1, sfx=[("whoosh", 0.0), ("pop", "thirty-three"), ("riser", ("horizon", -0.2)), ("hit", "slower")])
def hook(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    a = f.p(0.0, 0.5, "out")
    k8 = f.p("thirty-three", 0.6, "overshoot")
    # two sticks
    with moved(c, dx=(1 - a) * -80, alpha=a):
        ram_stick(c, f.cx, f.top + 130, 820, "DDR5-6000", color=BLUE)
    with moved(c, dx=(1 - a) * 80, alpha=a):
        ram_stick(c, f.cx, f.top + 400, 820, "DDR5-8000", color=GOLD, glow=k8 * (1 - f.p("slower", 0.4)))
    # spec bars (on the box)
    by = f.top + 620
    text(c, "ON THE BOX", 110, by, size=36, color=GREY, weight="bold", align="left", alpha=a)
    sp = f.p(0.3, 0.8, "out")
    rect(c, 110, by + 40, 560 * sp, 56, fill=BLUE, radius=10, alpha=a)
    text(c, "6000", 110 + 560 * sp + 20, by + 68, size=40, color=BLUE, weight="bold", align="left", alpha=a * sp)
    rect(c, 110, by + 116, 560 * sp * lerp(1, 4 / 3, k8), 56, fill=GOLD, radius=10, alpha=a)
    text(c, "8000", 110 + 560 * sp * lerp(1, 4 / 3, k8) + 20, by + 144, size=40, color=GOLD,
         weight="bold", align="left", alpha=a * sp)
    if k8 > 0:
        with moved(c, scale=max(k8, 0.001), about=(f.cx + 300, by - 4)):
            text(c, "+33%", f.cx + 300, by - 4, size=64, color=GOLD, weight="extrabold", glow=6)
    # in game
    g = f.p(("horizon", -0.1), 0.5)
    if g > 0:
        gy = f.top + 900
        text(c, "IN GAME (FPS)", 110, gy, size=36, color=GREY, weight="bold", align="left", alpha=g)
        fp = f.p(("horizon", 0.2), 0.8, "out")
        rect(c, 110, gy + 40, 560 * fp, 56, fill=BLUE, radius=10, alpha=g)
        text(c, "6000", 110 + 560 * fp + 20, gy + 68, size=40, color=BLUE, weight="bold", align="left", alpha=g * fp)
        drop = f.p("slower", 0.5, "in")
        w8 = 560 * fp * lerp(1.0, 0.92, drop)
        col = lerp_color(GOLD, RED, drop)
        shake = 10 * math.sin(f.t * 70) * max(0, 1 - f.since("slower") * 2.5) if f.after("slower") else 0
        with moved(c, dx=shake):
            rect(c, 110, gy + 116, w8, 56, fill=col, radius=10, alpha=g)
            text(c, "8000", 110 + w8 + 20, gy + 144, size=40, color=col, weight="bold", align="left", alpha=g * fp)
        s = f.p("slower", 0.45, "overshoot")
        if s > 0:
            with moved(c, scale=max(s, 0.001), about=(f.cx + 300, gy - 4)):
                text(c, "-8%", f.cx + 300, gy - 4, size=72, color=RED, weight="extrabold", glow=8)


# ------------------------------------------------------------------ 2. same CPU, same game
@VIDEO.scene("setup", lines=[
    Line("Same Ryzen. Same game. Six thousand beat eight thousand. Why?",
         show="Same Ryzen. Same game. 6000 beat 8000. Why?"),
], sfx=[("tick", "same"), ("tick", ("game", -0.1)), ("ding", "beat"), ("swell", "why")])
def setup(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    a = f.p(0.0, 0.5)
    chip(c, f.cx, f.top + 230, 260, color=BLUE, label="RYZEN", alpha=a, glow=0.4 * a)
    text(c, "Ryzen 9 9950X · 1080p", f.cx, f.top + 450, size=40, color=GREY, weight="medium", alpha=a)
    # scoreboard
    b = f.p("beat", 0.6, "out")
    y = f.top + 640
    for i, (lab, col, win) in enumerate([("DDR5-6000 CL28", BLUE, True), ("DDR5-8000 CL38", GOLD, False)]):
        yy = y + i * 170
        k = f.p(("same", 0.3 + i * 0.3), 0.5, "out")
        with moved(c, dx=(1 - k) * 120, alpha=k):
            rect(c, 110, yy, 860, 130, fill="#161B23", stroke=col, width=4, radius=20)
            text(c, lab, 160, yy + 65, size=52, color=col, weight="extrabold", align="left")
            if b > 0:
                mark = "WINS" if win else "LOSES"
                with moved(c, scale=max(overshoot(b), 0.001), about=(880, yy + 65)):
                    text(c, mark, 900, yy + 65, size=46, color=GREEN if win else RED, weight="extrabold",
                         align="right")
    text(c, "Source: TheFPSReview, Aug 6, 2026", f.cx, y + 345, size=30, color=GREY, weight="medium", alpha=f.p("beat", 0.5))
    q = f.p("why", 0.5, "overshoot")
    if q > 0:
        with moved(c, scale=max(q, 0.001), about=(f.cx, f.bottom - 60)):
            text(c, "WHY?", f.cx, f.bottom - 60, size=110, color=WHITE, weight="extrabold")


# ------------------------------------------------------------------ 3. the middleman
CPU_Y_OFF = 170
RAM_Y_OFF = 1000
MC_Y_OFF = 590


@VIDEO.scene("middleman", lines=[
    Line("Your CPU never talks to the RAM directly."),
    Line("It goes through a middleman: the memory controller."),
], sfx=[("whoosh", 0.0), ("pop", "middleman"), ("ding", "controller")])
def middleman(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    cpu_y, ram_y, mc_y = f.top + CPU_Y_OFF, f.top + RAM_Y_OFF, f.top + MC_Y_OFF
    a = f.p(0.0, 0.5)
    chip(c, f.cx, cpu_y, 220, color=BLUE, label="CPU", alpha=a)
    ram_stick(c, f.cx, ram_y, 760, "RAM", color=GOLD, alpha=a)
    m = f.p("middleman", 0.6, "overshoot")
    # before the middleman: a dashed direct line, crossed out
    if not f.after("middleman"):
        pass
    d = f.p(("directly", -0.3), 0.5)
    if d > 0 and m < 1:
        line(c, f.cx, cpu_y + 140, f.cx, ram_y - 110, color=GREY, width=5, progress=d, alpha=1 - m)
        x = f.p(("directly", 0.1), 0.3)
        line(c, f.cx - 60, mc_y - 60, f.cx + 60, mc_y + 60, color=RED, width=10, progress=x, alpha=1 - m)
        line(c, f.cx + 60, mc_y - 60, f.cx - 60, mc_y + 60, color=RED, width=10, progress=x, alpha=1 - m)
    if m > 0:
        with moved(c, scale=max(m, 0.001), about=(f.cx, mc_y)):
            box(c, f.cx, mc_y, 520, 170, fill="#1A2230", stroke=TEAL, width=5, radius=22)
            text(c, "MEMORY", f.cx, mc_y - 28, size=46, color=TEAL, weight="extrabold")
            text(c, "CONTROLLER", f.cx, mc_y + 28, size=46, color=TEAL, weight="extrabold")
        w = f.p("middleman", 0.6)
        line(c, f.cx - 40, cpu_y + 140, f.cx - 40, mc_y - 95, color=GREY, width=4, progress=w)
        line(c, f.cx + 40, mc_y - 95, f.cx + 40, cpu_y + 140, color=GREY, width=4, progress=w)
        line(c, f.cx - 40, mc_y + 95, f.cx - 40, ram_y - 110, color=GREY, width=4, progress=w)
        line(c, f.cx + 40, ram_y - 110, f.cx + 40, mc_y + 95, color=GREY, width=4, progress=w)
        # requests down (blue), answers up (gold)
        pk = f.p(("middleman", 0.4), 0.5)
        packets(c, f.cx - 40, cpu_y + 150, ram_y - 120, f.t, 3, BLUE, alpha=pk)
        packets(c, f.cx + 40, ram_y - 120, cpu_y + 150, f.t, 3, GOLD, alpha=pk, phase=0.3)
        text(c, "request", f.cx - 80, (cpu_y + mc_y) / 2, size=34, color=BLUE, weight="bold", align="right", alpha=pk)
        text(c, "answer", f.cx + 80, (cpu_y + mc_y) / 2, size=34, color=GOLD, weight="bold", align="left", alpha=pk)


# ------------------------------------------------------------------ 4. in sync at 6000
@VIDEO.scene("in_sync", lines=[
    Line("At six thousand, it keeps pace: three thousand megahertz, tick for tick.",
         show="At 6000, it keeps pace: 3000 MHz, tick for tick."),
], sfx=[("pop", "six"), ("tick", "tick"), ("tick", ("tick", 0.35)), ("ding", ("tick", 0.6))])
def in_sync(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    a = f.p(0.0, 0.5)
    text(c, "DDR5-6000", f.cx, f.top + 40, size=76, color=BLUE, weight="extrabold", alpha=a)
    rate = 1.2  # turns per second, same for both
    ang = f.t * rate * 2 * math.pi
    k = f.p("three", 0.6, "out")
    dial(c, 300, f.top + 420, 170, ang, GOLD, "RAM clock", f"{lerp(0, 3000, k):,.0f} MHz", alpha=a)
    dial(c, 780, f.top + 420, 170, ang, TEAL, "Controller", f"{lerp(0, 3000, k):,.0f} MHz", alpha=a)
    eq = f.p("three", 0.5)
    text(c, "=", f.cx, f.top + 420, size=110, color=WHITE, weight="bold", alpha=eq)
    # a smooth conveyor of answers
    s = f.p("tick", 0.5)
    if s > 0:
        y = f.top + 900
        rect(c, 110, y - 60, 860, 120, fill="#141920", stroke=DIM, width=3, radius=20, alpha=s)
        for i in range(9):
            x = 140 + ((f.t * 260 + i * 100) % 860)
            if x < 950:
                box(c, x, y, 60, 40, fill=GOLD, radius=6, alpha=s * min(1, (x - 120) / 60, (960 - x) / 60))
        text(c, "1 : 1  ·  no waiting", f.cx, y + 130, size=50, color=GREEN, weight="extrabold", alpha=s)


# ------------------------------------------------------------------ 5. half speed at 8000
@VIDEO.scene("half", lines=[
    Line("At eight thousand, it can't keep up, so it drops to half: two thousand megahertz.",
         show="At 8000, it can't keep up, so it drops to half: 2000 MHz."),
    Line("Faster RAM. Slower middleman."),
], sfx=[("pop", "eight"), ("riser", ("keep", -0.2)), ("hit", "half"), ("tick", "faster"), ("hit", "slower")])
def half(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    a = f.p(0.0, 0.5)
    text(c, "DDR5-8000", f.cx, f.top + 40, size=76, color=GOLD, weight="extrabold", alpha=a)
    h = f.p("half", 0.7, "smooth")
    ram_rate = 1.6
    mc_rate = lerp(1.6, 0.8, h)
    # integrate the controller angle so the hand doesn't jump
    t0 = f.cue("half")
    if f.t < t0:
        mc_ang = f.t * 1.6
    else:
        dt = f.t - t0
        mc_ang = t0 * 1.6 + 0.8 * dt + 0.8 * min(dt, 0.7) * 0.5
    struggle = 0.0
    if f.after(("keep", -0.1)) and not f.after("half"):
        struggle = 0.15 * math.sin(f.t * 40)
    dial(c, 300, f.top + 420, 170, f.t * ram_rate * 2 * math.pi, GOLD, "RAM clock", "4,000 MHz", alpha=a,
         glow=0.6)
    mhz = lerp(4000, 2000, h) if f.after(("keep", -0.1)) else 4000
    col = lerp_color(TEAL, RED, h)
    with moved(c, dx=struggle * 60):
        dial(c, 780, f.top + 420, 170, mc_ang * 2 * math.pi, col, "Controller", f"{mhz:,.0f} MHz", alpha=a,
             glow=h)
    hl = f.p("half", 0.4, "overshoot")
    if hl > 0:
        with moved(c, scale=max(hl, 0.001), about=(780, f.top + 720)):
            text(c, "½ SPEED", 780, f.top + 720, size=52, color=RED, weight="extrabold", glow=6)
    text(c, "≠", f.cx, f.top + 420, size=110, color=RED, weight="bold", alpha=f.p("half", 0.4))
    # the conveyor now jams: a queue piles up at the controller
    s = f.p(("keep", 0.2), 0.5)
    if s > 0:
        y = f.top + 900
        rect(c, 110, y - 60, 860, 120, fill="#141920", stroke=DIM, width=3, radius=20, alpha=s)
        gate = 640
        box(c, gate, y, 16, 140, fill=col, radius=6, alpha=s)
        # packets flow, but only pass the gate every 1/(rate) seconds
        q = int(clamp(f.since(("keep", 0.2)) / 2.5) * 5) + 1
        for i in range(q):
            box(c, gate - 50 - i * 70, y, 60, 40, fill=GOLD, radius=6, alpha=s)
        x = gate + 30 + ((f.t * 140) % 300)
        box(c, x, y, 60, 40, fill=GOLD, radius=6, alpha=s * min(1, (960 - x) / 60))
        text(c, "requests wait in line", f.cx, y + 130, size=50, color=RED, weight="extrabold",
             alpha=s * f.p("half", 0.5) * (1 - f.p(("faster", -0.3), 0.3)))
    # verdict line
    v = f.p("faster", 0.4)
    if v > 0:
        y2 = f.bottom - 70
        runs(c, [("RAM ", WHITE), ("faster ", GOLD)], f.cx - 200, y2, size=50, weight="extrabold", alpha=v)
        w = f.p("slower", 0.4, "overshoot")
        if w > 0:
            with moved(c, scale=max(w, 0.001), about=(f.cx + 230, y2)):
                runs(c, [("middleman ", WHITE), ("slower", RED)], f.cx + 230, y2, size=50, weight="extrabold")


# ------------------------------------------------------------------ 6. why games care
@VIDEO.scene("games", lines=[
    Line("Games need lots of tiny answers, fast. Every slow trip, your CPU just waits."),
], sfx=[("whoosh", 0.0), ("pop", "tiny"), ("pop", ("tiny", 0.25)), ("pop", ("tiny", 0.5)),
        ("tick", "waits")])
def games(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    # firehose: a thick stream, crossed out
    fh = f.p(0.0, 0.5)
    if fh > 0:
        y = f.top + 150
        alpha = fh * (1 - 0.6 * f.p("tiny", 0.4))
        rect(c, 120, y - 36, 840 * fh, 72, fill=BLUE, radius=36, alpha=alpha)
        for i in range(10):
            x = 120 + ((f.t * 900 + i * 90) % (840 * fh + 1))
            line(c, x, y - 20, x + 40, y - 20, color=WHITE, width=4, alpha=alpha * 0.5)
        text(c, "bandwidth", f.cx, y + 80, size=40, color=BLUE, weight="bold", alpha=alpha)
        x2 = f.p(("tiny", -0.3), 0.3)
        line(c, 120, y - 70, 960, y + 70, color=RED, width=10, progress=x2, alpha=fh)
    # tiny answers: many dots, each must round-trip
    ta = f.p("tiny", 0.5)
    if ta > 0:
        y0 = f.top + 400
        text(c, "latency", f.cx, y0 - 30, size=40, color=GOLD, weight="bold", alpha=ta)
        rnd = random.Random(4)
        for i in range(24):
            x = 160 + (i % 8) * 108
            yy = y0 + 50 + (i // 8) * 90
            on = f.p(("tiny", i * 0.05), 0.2, "overshoot")
            circle(c, x, yy, 18 * on, fill=GOLD, alpha=ta)
    # CPU timeline: work vs wait
    w = f.p("every", 0.5)
    if w > 0:
        ty = f.top + 860
        text(c, "CPU, one frame", 110, ty - 40, size=38, color=GREY, weight="bold", align="left", alpha=w)
        prog = clamp(f.since("every") / 2.4) if f.after("every") else 0
        segs = [(0.12, "work"), (0.10, "wait"), (0.1, "work"), (0.14, "wait"), (0.08, "work"),
                (0.12, "wait"), (0.12, "work"), (0.22, "wait")]
        x = 110
        total = 860
        acc = 0.0
        for frac, kind in segs:
            if acc >= prog:
                break
            seg = min(frac, prog - acc)
            col = BLUE if kind == "work" else RED
            rect(c, x, ty, total * seg, 90, fill=col, radius=6, alpha=w)
            if kind == "wait" and seg > 0.06:
                text(c, "wait", x + total * seg / 2, ty + 45, size=32, color=BG, weight="extrabold", alpha=w)
            x += total * frac
            acc += frac
        rect(c, 110, ty, total, 90, stroke=DIM, width=3, radius=6, alpha=w)
        wt = f.p("waits", 0.4, "overshoot")
        if wt > 0:
            with moved(c, scale=max(wt, 0.001), about=(f.cx, ty + 200)):
                text(c, "slower middleman = longer waits", f.cx, ty + 200, size=48, color=RED,
                     weight="extrabold")


# ------------------------------------------------------------------ 7. verdict
@VIDEO.scene("verdict", lines=[
    Line("For gaming on Ryzen, reviewers say: get low-latency six thousand.",
         show="For gaming on Ryzen, reviewers say: get low-latency 6000."),
    Line("On a big-cache X three D chip, slow versus fast RAM was just two percent.",
         show="On a big-cache X3D chip, slow vs fast RAM was just ~2%."),
], sfx=[("whoosh", 0.0), ("ding", "six"), ("pop", "three"), ("hit", "two")], pad_out=0.4)
def verdict(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    a = f.p("six", 0.6, "overshoot")
    text(c, "GAMING ON RYZEN", f.cx, f.top + 60, size=56, color=GREY, weight="extrabold", alpha=f.p(0.0, 0.5))
    if a > 0:
        with moved(c, scale=max(a, 0.001), about=(f.cx, f.top + 270)):
            ram_stick(c, f.cx, f.top + 250, 800, "DDR5-6000", color=BLUE, glow=0.8)
            text(c, "low latency (CL28-30)", f.cx, f.top + 420, size=46, color=GREEN, weight="extrabold")
    b = f.p("three", 0.5)
    if b > 0:
        y = f.top + 620
        chip(c, 250, y + 170, 200, color=PURPLE, label="X3D", label_color=WHITE, alpha=b, glow=0.6 * b)
        text(c, "Ryzen 7 9800X3D", 250, y + 360, size=34, color=GREY, weight="medium", alpha=b)
        # two bars: slowest vs fastest kit, nearly equal
        k = f.p("two", 0.7, "out")
        base = y + 330
        bar(c, 560, base, 150, 300 * 0.98, color=GREY, progress=k, label="slow RAM", alpha=b)
        bar(c, 800, base, 150, 300, color=GOLD, progress=k, label="fast RAM", alpha=b)
        if f.after("two"):
            text(c, "~2%", 680, y - 30, size=90, color=GOLD, weight="extrabold", glow=8,
                 alpha=f.p("two", 0.4))
        text(c, "TechPowerUp test, Sep 2026", 680, base + 110, size=30, color=GREY, weight="medium", alpha=k)
