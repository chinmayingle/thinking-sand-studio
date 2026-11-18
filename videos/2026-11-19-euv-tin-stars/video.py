"""Short: your GPU was printed with light from 50,000 tiny explosions a second (EUV lithography).

Lane: proven (hardware). Mesmerizing-animation experiment (Nov 18, 2026).

Facts (see claude/euv-tin-stars-short.md in the CC project):
- ASML, "The hottest thing about ASML machines": EUV light is 13.5 nm; molten tin droplets
  shoot from a generator at 70 m/s; a low-intensity pulse flattens each into a pancake; a more
  powerful pulse vaporizes it into a plasma at about 500,000 K, hotter than the surface of the
  Sun; repeated 50,000 times every second.
- ZEISS SMT: EUV light is absorbed by air and glass, so the optics run in a vacuum and use only
  mirrors. Visible light is roughly 400-800 nm (400 / 13.5 = about 30x).
- TechPowerUp: the RTX 5090's GB202 has 92.2 billion transistors, made on TSMC 4N, an
  Nvidia-specific variant of TSMC 5 nm EUV. (EUV prints the finest layers; not every layer.)
- Sun's surface about 5,800 K (NASA: 5,772 K).
Build: python -m studio.make videos/2026-11-19-euv-tin-stars
"""
import math
import random

import skia

from studio import *

VIDEO = Video("euv-tin-stars", format="short", speed=1.07,
              question="Did you know chips are printed with exploding tin?")

TIN = "#FFB25B"        # molten tin glow
TIN_CORE = "#FFF1D6"
EUV = "#B48CFF"        # extreme ultraviolet, drawn as violet
LASER = "#FC6255"
HOT = "#FFFFFF"


# ------------------------------------------------------------------ helpers
def oval(c, cx, cy, rx, ry, color, alpha=1.0, blur=0.0):
    c.drawOval(skia.Rect.MakeLTRB(cx - rx, cy - ry, cx + rx, cy + ry), paint(color, alpha, blur=blur))


def droplet(c, x, y, r, alpha=1.0, trail=0.0):
    """A molten tin drop with a soft glow and an optional motion trail above it."""
    if trail > 0:
        for i in range(6):
            k = i / 6
            circle(c, x, y - trail * k, r * (1 - 0.12 * i), fill=TIN, alpha=alpha * 0.18 * (1 - k))
    circle(c, x, y, r * 2.4, fill=TIN, alpha=0.35 * alpha, blur=r * 1.2)
    circle(c, x, y, r, fill=TIN, alpha=alpha)
    circle(c, x - r * 0.3, y - r * 0.3, r * 0.4, fill=TIN_CORE, alpha=0.9 * alpha)


def burst(c, x, y, k, size=1.0, seed=0, rays=14):
    """A tin plasma flash: k = 0 at the hit, 1 when it has faded."""
    if k < 0 or k > 1:
        return
    rnd = random.Random(seed)
    fade = (1 - k) ** 1.6
    # violet halo, white core
    circle(c, x, y, size * (60 + 220 * ease_out(k)), fill=EUV, alpha=0.55 * fade, blur=size * 60)
    circle(c, x, y, size * (20 + 70 * ease_out(min(1, k * 2))), fill=HOT, alpha=fade, blur=size * 14)
    circle(c, x, y, size * 16 * (1 - k), fill=HOT, alpha=fade)
    # rays
    for i in range(rays):
        a = i / rays * 2 * math.pi + rnd.random() * 0.3
        L = size * (90 + 260 * rnd.random()) * ease_out(k)
        r0 = size * 20
        line(c, x + r0 * math.cos(a), y + r0 * math.sin(a), x + L * math.cos(a), y + L * math.sin(a),
             color=EUV, width=size * (3 + 3 * rnd.random()), alpha=0.8 * fade)
    # sparks
    for i in range(22):
        a = rnd.random() * 2 * math.pi
        v = size * (150 + 380 * rnd.random())
        d = v * ease_out(k)
        circle(c, x + d * math.cos(a), y + d * math.sin(a), size * (3 + 4 * rnd.random()) * (1 - k),
               fill=TIN_CORE if i % 3 else EUV, alpha=fade)


def beam(c, x1, y1, x2, y2, color, width, alpha=1.0):
    line(c, x1, y1, x2, y2, color=color, width=width * 4, alpha=0.25 * alpha)
    line(c, x1, y1, x2, y2, color=color, width=width, alpha=alpha)
    line(c, x1, y1, x2, y2, color=HOT, width=max(1.5, width * 0.3), alpha=0.8 * alpha)


def stars_bg(c, f, n=70, seed=3, alpha=1.0):
    """Faint twinkling dust so the vacuum chamber never looks flat."""
    rnd = random.Random(seed)
    for i in range(n):
        x, y = rnd.random() * f.W, f.top + rnd.random() * (f.bottom - f.top)
        tw = 0.5 + 0.5 * math.sin(f.T * (1 + 2 * rnd.random()) + i)
        circle(c, x, y, 1.5 + 2 * rnd.random(), fill=EUV if i % 4 == 0 else WHITE, alpha=0.18 * tw * alpha)


# ------------------------------------------------------------------ 1. hook
@VIDEO.scene("hook", lines=[
    Line("To print the chip in your GPU, a machine blows up fifty thousand drops of molten tin.",
         show="To print the chip in your GPU, a machine blows up 50,000 drops of molten tin."),
    Line("Every single second."),
], pad_in=0.05, sfx=[("whoosh", 0.0), ("hit", ("blows", 0.1)), ("riser", ("fifty", -0.3)), ("hit", "every"),
                      ("hit", "single"), ("hit", "second")])
def hook(f):
    c = f.c
    stars_bg(c, f)
    nx, fy = f.cx, f.top + 470          # nozzle x, focus point y
    # the droplet generator
    box(c, nx, f.top + 30, 120, 60, fill="#1A2029", stroke=GREY, width=3, radius=10)
    # a steady stream of drops, each exploding at the focus (sped-up time, not real time)
    period = 0.30
    speed = 900
    for k in range(-1, int(f.t / period) + 2):
        t0 = k * period
        age = f.t - t0
        if age < 0:
            continue
        y = f.top + 70 + speed * age
        if y < fy:
            droplet(c, nx, y, 13, trail=60)
        else:
            hit_age = (y - fy) / speed
            burst(c, nx, fy, hit_age / 0.55, size=0.9, seed=k)
    # laser arrives from the right at the focus
    beam(c, f.W, fy - 260, nx + 4, fy, LASER, 4, alpha=0.5 + 0.3 * pulse(f.t * 3, 0.3))
    # the counter
    k = f.p("fifty", 1.1, "out")
    if k > 0:
        number(c, lerp(0, 50000, k), f.cx, f.top + 860, fmt="{:,.0f}", size=190, color=GOLD, glow=10)
        text(c, "drops of molten tin", f.cx, f.top + 990, size=50, color=WHITE, weight="bold", alpha=k)
    for i, w in enumerate(["every", "single", "second"]):
        a = f.p(w, 0.25, "overshoot")
        if a > 0:
            x = f.cx - 330 + i * 330
            with moved(c, scale=max(a, 0.001), about=(x, f.bottom - 30)):
                text(c, w.upper(), x, f.bottom - 30, size=62, color=TIN if i < 2 else GOLD, weight="extrabold")


# ------------------------------------------------------------------ 2. slow motion: the pancake
@VIDEO.scene("pancake", lines=[
    Line("Each drop flies at seventy metres a second.",
         show="Each drop flies at 70 m/s."),
    Line("A weak laser pulse squashes it flat, like a pancake."),
], pad_in=0.1, sfx=[("swell", 0.0), ("tick", "seventy"), ("whoosh", "weak"), ("pop", "flat")])
def pancake(f):
    c = f.c
    stars_bg(c, f, seed=5)
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom, alpha=0.05)
    text(c, "SLOW MOTION", f.cx, f.top + 40, size=40, color=GREY, weight="bold", alpha=f.p(0.0, 0.5))
    cx, cy = f.cx, f.cy - 40
    hit = f.cue("weak")
    # the drop drifts down to the focus, arriving as the pulse fires
    arrive = clamp(f.t / max(0.1, hit))
    y = lerp(f.top + 160, cy, smooth(arrive))
    sq = f.p("squashes", 0.5, "out")
    rx, ry = lerp(70, 210, sq), lerp(70, 26, sq)
    if sq <= 0:
        droplet(c, cx, y, 70, trail=lerp(160, 0, arrive))
    else:
        oval(c, cx, cy, rx * 1.6, ry * 2.6, TIN, 0.3, blur=40)
        oval(c, cx, cy, rx, ry, TIN)
        oval(c, cx - rx * 0.2, cy - ry * 0.35, rx * 0.5, ry * 0.3, TIN_CORE, 0.8)
    # speed label
    s = f.p("seventy", 0.5, "overshoot")
    if s > 0 and sq < 1:
        with moved(c, scale=max(s, 0.001), about=(cx + 260, y)):
            text(c, "70 m/s", cx + 260, y, size=76, color=GOLD, weight="extrabold")
        arrow(c, cx + 150, y - 60, cx + 150, y + 60, color=GOLD, width=6, progress=s)
    # pulse 1 from the left
    if f.after("weak"):
        a = 1 - clamp(f.since("weak") / 0.6)
        beam(c, 0, cy, cx - 60, cy, LASER, 5, alpha=a)
        circle(c, cx - 70, cy, 40, fill=LASER, alpha=0.6 * a, blur=20)
    lab = f.p("weak", 0.5)
    if lab > 0:
        text(c, "pulse 1: weak", 70, cy + 210, size=48, color=LASER, weight="bold", align="left", alpha=lab)
    p = f.p("pancake", 0.5, "overshoot")
    if p > 0:
        with moved(c, scale=max(p, 0.001), about=(f.cx, f.bottom - 60)):
            text(c, "a tin pancake", f.cx, f.bottom - 60, size=80, color=TIN, weight="extrabold")


# ------------------------------------------------------------------ 3. plasma
@VIDEO.scene("plasma", lines=[
    Line("Then a stronger pulse blasts it into plasma, about five hundred thousand kelvin.",
         show="Then a stronger pulse blasts it into plasma, about 500,000 kelvin."),
    Line("Hotter than the surface of the Sun."),
], pad_in=0.1, sfx=[("riser", ("stronger", -0.3)), ("hit", "blasts"), ("swell", "plasma"), ("tick", "five"), ("ding", "sun")])
def plasma(f):
    c = f.c
    stars_bg(c, f, seed=7)
    cx, cy = f.cx, f.top + 400
    blast = f.cue("blasts")
    if f.t < blast:
        oval(c, cx, cy, 210, 26, TIN)
        oval(c, cx, cy, 340, 70, TIN, 0.3, blur=40)
        k = f.p("stronger", 0.4)
        beam(c, 0, cy - 160 * (1 - k), cx - 100, cy, LASER, 12, alpha=k)
    else:
        a = f.since("blasts")
        burst(c, cx, cy, min(0.55, a / 2.2), size=1.6, seed=11, rays=22)
        # a breathing plasma ball that stays
        breathe = 0.85 + 0.15 * math.sin(f.t * 9)
        circle(c, cx, cy, 170 * breathe, fill=EUV, alpha=0.45, blur=70)
        circle(c, cx, cy, 70 * breathe, fill=HOT, alpha=0.95, blur=24)
        text(c, "PLASMA", cx, cy + 250, size=60, color=EUV, weight="extrabold", alpha=clamp(a * 2))
    # temperature bars: Sun's surface vs the plasma (to scale)
    k = f.p("five", 1.2, "out")
    if k > 0:
        base = f.bottom - 40
        x0, w = 120, 840
        text(c, "temperature, to scale", f.cx, base - 330, size=36, color=GREY, alpha=k)
        number(c, lerp(0, 500000, k), x0, base - 250, fmt="{:,.0f} K", size=72, color=EUV, align="left")
        rect(c, x0, base - 190, w * k, 56, fill=EUV, radius=12)
        text(c, "tin plasma", x0 + w, base - 230, size=40, color=EUV, weight="bold", align="right", alpha=k)
        s = f.p("sun", 0.6, "out")
        if s > 0:
            rect(c, x0, base - 80, max(6, w * 5800 / 500000), 56, fill=GOLD, radius=6, alpha=s)
            text(c, "Sun's surface ≈ 5,800 K", x0 + 40, base - 52, size=40, color=GOLD, weight="bold",
                 align="left", alpha=s)


# ------------------------------------------------------------------ 4. the light
def wave(c, x0, x1, y, wl, amp, phase, color, width, alpha=1.0, progress=1.0):
    pts = []
    n = int((x1 - x0) / 3)
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        pts.append((x, y + amp * math.sin((x - x0) / wl * 2 * math.pi - phase)))
    p = polyline(pts)
    stroke_path(c, p, color=color, width=width * 3, alpha=0.2 * alpha, progress=progress)
    stroke_path(c, p, color=color, width=width, alpha=alpha, progress=progress)


@VIDEO.scene("light", lines=[
    Line("It glows with extreme ultraviolet light: waves just thirteen point five nanometres long.",
         show="It glows with extreme ultraviolet light: waves just 13.5 nanometres long."),
    Line("About thirty times shorter than visible light."),
], pad_in=0.1, sfx=[("swell", 0.0), ("pop", "thirteen"), ("pop", "thirty")])
def light(f):
    c = f.c
    stars_bg(c, f, seed=9)
    x0, x1 = 90, 990
    px_per_nm = 600 / 400                     # visible violet (400 nm) drawn 600 px long
    ph = f.t * 5
    # EUV wave appears first
    e = f.p(0.2, 1.4, "linear")
    y_e = f.top + 330
    wave(c, x0, x1, y_e, 13.5 * px_per_nm, 70, ph * 3, EUV, 4, progress=e)
    text(c, "EUV", x0, y_e - 130, size=60, color=EUV, weight="extrabold", align="left", alpha=e)
    k = f.p("thirteen", 0.6, "overshoot")
    if k > 0:
        with moved(c, scale=max(k, 0.001), about=(x1, y_e - 130)):
            text(c, "13.5 nm", x1, y_e - 130, size=64, color=WHITE, weight="extrabold", align="right")
    # visible light for comparison
    v = f.p("thirty", 1.0, "linear")
    y_v = f.top + 760
    if v > 0:
        wave(c, x0, x1, y_v, 400 * px_per_nm, 110, ph, "#8F7BFF", 6, progress=v)
        text(c, "visible (violet)", x0, y_v - 170, size=48, color="#8F7BFF", weight="bold", align="left",
             alpha=v)
        text(c, "400 nm", x1, y_v - 170, size=48, color=WHITE, weight="bold", align="right", alpha=v)
        # one EUV wavelength vs one visible wavelength
        brace(c, x0, x0 + 400 * px_per_nm, y_v + 160, label="1 visible wave", color=GREY, size=38,
              progress=v)
        q = f.p(("thirty", 0.6), 0.5, "overshoot")
        if q > 0:
            with moved(c, scale=max(q, 0.001), about=(f.cx, f.bottom - 60)):
                runs(c, [("≈30× ", GOLD), ("shorter", WHITE)], f.cx, f.bottom - 60, size=96, weight="extrabold")


# ------------------------------------------------------------------ 5. vacuum and mirrors
@VIDEO.scene("mirrors", lines=[
    Line("But air and glass swallow this light."),
    Line("So it travels through a vacuum, bounced only by mirrors."),
], pad_in=0.1, sfx=[("tick", "air"), ("pop", "swallow"), ("whoosh", "vacuum"), ("tick", "bounced"),
        ("tick", ("mirrors", 0.2)), ("ding", ("mirrors", 0.6))])
def mirrors(f):
    c = f.c
    stars_bg(c, f, seed=13, alpha=f.p("vacuum", 0.8))
    # part 1: a ray dies inside a glass block
    g = 1 - f.p("so", 0.4)
    if g > 0:
        with moved(c, alpha=g):
            gx, gy = f.cx + 120, f.cy - 60
            box(c, gx, gy, 300, 420, fill="#9FD3E6", alpha=0.12, radius=14)
            box(c, gx, gy, 300, 420, stroke="#CFE8F2", width=4, radius=14, alpha=0.7)
            text(c, "glass", gx, gy + 260, size=44, color="#CFE8F2", weight="bold")
            # ray: travels in from the left, fades inside the glass
            p = f.p("air", 0.8, "linear")
            xe = lerp(60, gx + 40, p)
            beam(c, 60, gy, min(xe, gx - 150), gy, EUV, 8)
            if xe > gx - 150:
                fade = clamp((xe - (gx - 150)) / 190)
                beam(c, gx - 150, gy, xe, gy, EUV, 8, alpha=1 - fade)
            s = f.p("swallow", 0.4, "overshoot")
            if s > 0:
                with moved(c, scale=max(s, 0.001), about=(f.cx, f.top + 120)):
                    text(c, "absorbed", f.cx, f.top + 120, size=86, color=RED, weight="extrabold")
    # part 2: a zigzag of mirrors in a vacuum
    m = f.p("so", 0.5)
    if m > 0:
        text(c, "VACUUM", f.cx, f.top + 40, size=44, color=GREY, weight="bold", alpha=f.p("vacuum", 0.5))
        pts = [(140, f.top + 160), (900, f.top + 360), (180, f.top + 600), (900, f.top + 820),
               (f.cx, f.bottom - 80)]
        for (x, y) in pts[1:-1]:
            side = 1 if x > f.cx else -1
            # a curved gold mirror facing the beam
            path = skia.Path()
            path.moveTo(x + side * 20, y - 110)
            path.quadTo(x - side * 30, y, x + side * 20, y + 110)
            c.drawPath(path, paint(GOLD, 0.35 * m, stroke=True, width=26, blur=8))
            c.drawPath(path, paint(GOLD, m, stroke=True, width=12))
        circle(c, pts[0][0], pts[0][1], 60, fill=EUV, alpha=0.6 * m, blur=30)
        circle(c, pts[0][0], pts[0][1], 22, fill=HOT, alpha=m)
        b = f.p("bounced", max(0.8, f.line_end(1) - f.cue("bounced")), "linear")
        if b > 0:
            path = polyline(pts)
            stroke_path(c, path, color=EUV, width=26, alpha=0.25, progress=b, blur=6)
            stroke_path(c, path, color=EUV, width=8, progress=b)
            stroke_path(c, path, color=HOT, width=3, progress=b, alpha=0.8)
        if b >= 1:
            circle(c, pts[-1][0], pts[-1][1], 40 + 10 * pulse(f.t, 0.6), fill=EUV, alpha=0.7, blur=18)


# ------------------------------------------------------------------ 6. the wafer
def die_lines(c, x, y, s, seed, p, color=EUV):
    """Manhattan circuit lines drawn into one die."""
    rnd = random.Random(seed)
    for i in range(14):
        px, py = x + rnd.random() * s, y + rnd.random() * s
        pts = [(px, py)]
        for j in range(4):
            if j % 2 == 0:
                px = clamp(px + (rnd.random() - 0.5) * s * 0.7, x + 6, x + s - 6)
            else:
                py = clamp(py + (rnd.random() - 0.5) * s * 0.7, y + 6, y + s - 6)
            pts.append((px, py))
        stroke_path(c, polyline(pts), color=color, width=max(1.5, s * 0.012), progress=p, alpha=0.9)


@VIDEO.scene("wafer", lines=[
    Line("Then it draws the finest patterns onto silicon."),
    Line("Like the R T X fifty-ninety's chip: ninety-two billion transistors.",
         show="Like the RTX 5090's chip: 92 billion transistors."),
], pad_in=0.1, sfx=[("whoosh", 0.0), ("riser", ("draws", 0.0)), ("pop", "fifty-ninety's"), ("hit", "ninety-two")])
def wafer(f):
    c = f.c
    stars_bg(c, f, seed=17)
    zoom = f.p("like", 1.4, "smooth")
    wx, wy, R = f.cx, f.top + 470, 420
    die = 84
    target = (wx + die * 1, wy - die * 1)     # the die we zoom into (its top-left corner)
    sc = 1 + 6 * zoom * zoom
    with moved(c, scale=sc, about=(target[0] + die / 2, target[1] + die / 2),
               dx=(f.cx - target[0] - die / 2) * smooth(zoom), dy=(wy - target[1] - die / 2) * smooth(zoom)):
        # wafer disc with a soft sheen
        circle(c, wx, wy, R + 30, fill="#3A4252", alpha=0.6, blur=30)
        circle(c, wx, wy, R, fill="#232A35")
        circle(c, wx, wy, R, stroke="#5A6578", width=4)
        # a light band scanning down; dies light up after it passes
        scan = f.p("draws", max(1.0, f.line_end(0) - f.cue("draws")), "linear")
        sy = lerp(wy - R, wy + R, scan)
        c.save()
        c.clipPath(skia.Path().addCircle(wx, wy, R - 6), skia.ClipOp.kIntersect, True)
        n = int(R * 2 / die) + 2
        for i in range(-n // 2, n // 2 + 1):
            for j in range(-n // 2, n // 2 + 1):
                x, y = wx + i * die, wy + j * die
                if (x + die / 2 - wx) ** 2 + (y + die / 2 - wy) ** 2 > (R - 20) ** 2:
                    continue
                lit = y + die < sy
                rect(c, x + 3, y + 3, die - 6, die - 6, fill="#2E3644" if not lit else "#33294D", radius=4)
                if lit:
                    die_lines(c, x + 3, y + 3, die - 6, seed=i * 31 + j, p=clamp((sy - y - die) / 120))
        if 0 < scan < 1:
            rect(c, wx - R, sy - 10, 2 * R, 20, fill=EUV, alpha=0.8, blur=12)
            rect(c, wx - R, sy - 2, 2 * R, 4, fill=HOT, alpha=0.9)
        c.restore()
    if zoom > 0.6:
        a = clamp((zoom - 0.6) / 0.4)
        rect(c, 0, f.top - 40, f.W, 140, fill=BG, alpha=0.85 * a, blur=20)
        text(c, "RTX 5090 chip (GB202)", f.cx, f.top + 40, size=46, color=WHITE, weight="bold", alpha=a)
    k = f.p("ninety-two", 1.0, "out")
    if k > 0:
        rect(c, 0, f.bottom - 250, f.W, 280, fill=BG, alpha=0.88 * min(1, k * 3), blur=24)
        number(c, lerp(0, 92.2, k), f.cx, f.bottom - 150, fmt="{:.1f} billion", size=110, color=GOLD, glow=8)
        text(c, "transistors", f.cx, f.bottom - 50, size=54, color=WHITE, weight="bold", alpha=k)


# ------------------------------------------------------------------ 7. close
@VIDEO.scene("close", lines=[
    Line("Your GPU is sand, taught to think by tiny artificial suns."),
], pad_in=0.1, pad_out=0.5, sfx=[("swell", 0.0), ("pop", "sand"), ("ding", "suns")])
def close(f):
    c = f.c
    stars_bg(c, f, seed=21)
    cx, cy, s = f.cx, f.cy - 80, 380
    gather = f.p("sand", max(1.0, f.cue("suns") - f.cue("sand")), "smooth")
    rnd = random.Random(4)
    # grains fly from scattered spots into the chip's square
    for i in range(420):
        sx, sy = rnd.random() * f.W, f.top + rnd.random() * (f.bottom - f.top)
        tx, ty = cx - s / 2 + rnd.random() * s, cy - s / 2 + rnd.random() * s
        k = clamp(gather * 1.3 - rnd.random() * 0.3)
        x, y = lerp(sx, tx, smooth(k)), lerp(sy, ty, smooth(k))
        circle(c, x, y, 3.5, fill=SAND[i % 4], alpha=0.85 * (1 - 0.7 * clamp((gather - 0.85) / 0.15)))
    if gather > 0.8:
        a = clamp((gather - 0.8) / 0.2)
        chip(c, cx, cy, s, color=GOLD, glow=a * (0.7 + 0.3 * pulse(f.t)), alpha=a)
    # little suns flashing around it
    if f.after("artificial"):
        for i in range(6):
            ang = i / 6 * 2 * math.pi + f.t * 0.6
            x, y = cx + 360 * math.cos(ang), cy + 360 * math.sin(ang)
            k = (f.t * 1.7 + i / 6) % 1
            burst(c, x, y, k, size=0.35, seed=i)
    q = f.p("taught", 0.6)
    if q > 0:
        text(c, "sand, taught to think", f.cx, f.bottom - 60, size=74, color=WHITE, weight="extrabold", alpha=q)
