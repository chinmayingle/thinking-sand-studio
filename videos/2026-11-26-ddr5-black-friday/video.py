"""Short: No RAM deals this Black Friday. 32 GB of DDR5: $447, once $72. AI is eating the wafers.

Lane: proven (hardware: the RAM in the viewer's PC). Peg: Black Friday, Nov 27, 2026.

Facts (see claude/ddr5-black-friday-short.md in the CC project):
- Tom's Hardware RAM Price Index (updated Oct 26, 2026): cheapest 32 GB DDR5-6000 kit $447; lowest
  price ever tracked $72. Tom's Hardware (Jul 28, 2026): Crucial Pro 32 GB DDR5-6000 $90 on Prime Day 2025.
- 3DCenter "Speicherkrise Preisindex November 2026" (via Shazoo Nov 17, Pause Hardware Nov 16,
  Wccftech Nov 16, Guru3D): German DDR5 retail index at 607% of July 2025; a 2x48 GB DDR5-6400 kit
  about EUR 304 -> EUR 2,779 (9.1x).
- TrendForce (press release Sep 30, 2026): conventional DRAM contract prices +10-15% QoQ in Q4 2026,
  as suppliers move advanced-process capacity to server products. TrendForce DRAM bulletin
  (Nov 18, 2026): prices keep rising, more slowly each quarter.
- Micron (Raghu Sreeramaneni, Hot Chips 2026, Aug 23; Tom's Hardware Aug 25, 2026): HBM takes roughly
  three times the wafer area of DDR5 for the same capacity.
Build: python -m studio.make videos/2026-11-26-ddr5-black-friday
"""
import math

from studio import *

VIDEO = Video("ddr5-black-friday", format="short", speed=1.15,
              question="What did you pay for your RAM?")
VIDEO.endcard_lines = [
    Line("What did you pay for your RAM, and when? Tell me in the comments.",
         show="What did you pay for your RAM, and when? Tell me in the comments."),
    Line("And if this helped, like, share, and subscribe to The Thinking Sand.",
         show="If this helped: like, share, and subscribe to The Thinking Sand."),
]

PANEL = "#161B23"


def stick(c, cx, cy, w=640, h=150, color=GREEN, alpha=1.0, chips=8):
    """A RAM stick: green PCB, black chips, gold contacts."""
    x, y = cx - w / 2, cy - h / 2
    rect(c, x, y, w, h, fill="#1F5A3A", radius=8, alpha=alpha)
    cw = (w - 60) / chips
    for i in range(chips):
        rect(c, x + 30 + i * cw + 6, y + 20, cw - 12, h - 62, fill="#111418", radius=4, alpha=alpha)
    for i in range(int(w / 14)):
        rect(c, x + 12 + i * 14, y + h - 26, 8, 20, fill=GOLD, radius=1, alpha=alpha * 0.9)
    rect(c, cx - 8, y + h - 30, 16, 30, fill=BG, alpha=alpha)   # the notch


def wafer(c, cx, cy, r, die, color, progress=1.0, alpha=1.0, label=None):
    """A round wafer filled with square dies of size `die` (fewer, bigger dies = less memory)."""
    circle(c, cx, cy, r, fill="#20262F", alpha=alpha)
    circle(c, cx, cy, r, stroke=GREY, width=3, alpha=alpha * 0.7)
    n = int(2 * r / die) + 2
    cells = []
    for i in range(-n, n):
        for j in range(-n, n):
            x = cx - die / 2 + i * die
            y = cy - die / 2 + j * die
            corners = [(x, y), (x + die, y), (x, y + die), (x + die, y + die)]
            if all((px - cx) ** 2 + (py - cy) ** 2 <= (r - 6) ** 2 for px, py in corners):
                cells.append((x, y))
    cells.sort(key=lambda p: (p[1], p[0]))
    shown = int(len(cells) * clamp(progress))
    for x, y in cells[:shown]:
        rect(c, x + 3, y + 3, die - 6, die - 6, fill=color, radius=3, alpha=alpha * 0.9)
    if label:
        text(c, label, cx, cy + r + 50, size=40, color=color, weight="extrabold", alpha=alpha)
    return len(cells)


# ------------------------------------------------------------------ 1. hook
@VIDEO.scene("hook", lines=[
    Line("Thirty-two gigs of DDR5 once sold for seventy-two dollars.",
         show="32 GB of DDR5 once sold for $72."),
    Line("By late October, the cheapest kit cost four hundred forty-seven.",
         show="By late October, the cheapest kit cost $447."),
], pad_in=0.1, pad_out=0.3, sfx=[("whoosh", 0.0), ("pop", "seventy-two"), ("riser", ("four", -0.6)),
                                 ("hit", "forty-seven")])
def hook(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    a = f.p(0.05, 0.5, "out")
    with moved(c, dy=(1 - a) * 60, alpha=a):
        stick(c, f.cx, f.top + 170)
        text(c, "32 GB DDR5-6000", f.cx, f.top + 310, size=48, color=WHITE, weight="extrabold")
    # price bars from one baseline
    base = f.top + 950
    k1 = f.p("seventy-two", 0.6, "out")
    k2 = f.p("four", 1.0, "out")
    H447 = 480
    h72 = H447 * 72 / 447
    if k1 > 0:
        bar(c, 330, base, 240, h72 * k1, color=GREY, label="lowest ever", value="$72")
    if k2 > 0:
        v = lerp(72, 447, k2)
        bar(c, 750, base, 240, max(H447 * v / 447, 1), color=GOLD, label="late Oct 2026",
            value=f"${v:.0f}")
    g = f.p(("forty-seven", 0.2), 0.5, "overshoot")
    if g > 0:
        with moved(c, scale=max(g, 0.001), about=(f.cx, f.top + 1110)):
            text(c, "≈ 6×", f.cx, f.top + 1110, size=96, color=RED, weight="extrabold", glow=8)
    text(c, "Tom's Hardware RAM Price Index, Oct 26, 2026", f.cx, f.top + 1190, size=26, color=GREY,
         weight="medium", alpha=f.p(("forty-seven", 0.4), 0.5))


# ------------------------------------------------------------------ 2. Europe: 9x
@VIDEO.scene("europe", lines=[
    Line("In Germany, a ninety-six gig kit went from three hundred euros to almost twenty-eight hundred.",
         show="In Germany, a 96 GB kit went from €304 to €2,779."),
    Line("Nine times the price. No Black Friday sale fixes that.",
         show="9× the price. No Black Friday sale fixes that."),
], sfx=[("whoosh", 0.0), ("pop", "three"), ("riser", ("almost", -0.4)), ("hit", "nine"),
        ("tick", "black")])
def europe(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    a = f.p(0.0, 0.5, "out")
    text(c, "2 × 48 GB DDR5-6400 · Germany", f.cx, f.top + 50, size=42, color=GREY, weight="extrabold",
         alpha=a)
    # 9 coin stacks: one for last year, nine for now
    k = f.p("almost", 1.6, "out")
    unit = 62
    y0 = f.top + 760
    old = f.p("three", 0.5, "overshoot")
    if old > 0:
        with moved(c, scale=max(old, 0.001), about=(250, y0)):
            rect(c, 250 - 80, y0 - unit, 160, unit - 8, fill=GREY, radius=10)
        text(c, "€304", 250, y0 + 60, size=56, color=WHITE, weight="extrabold", alpha=clamp(old))
        text(c, "a year earlier", 250, y0 + 115, size=30, color=GREY, weight="medium", alpha=clamp(old))
    n = 9.14 * k
    for i in range(9):
        fill = clamp(n - i)
        if fill > 0:
            yy = y0 - (i + 1) * unit
            rect(c, 720 - 110, yy + unit * (1 - fill), 220, (unit - 8) * fill, fill=GOLD, radius=10,
                 alpha=0.6 + 0.4 * fill)
    if k > 0:
        text(c, f"€{lerp(304, 2779, k):,.0f}", 720, y0 + 60, size=64, color=GOLD, weight="extrabold")
        text(c, "Nov 2026", 720, y0 + 115, size=30, color=GREY, weight="medium")
    g = f.p("nine", 0.5, "overshoot")
    if g > 0:
        with moved(c, scale=max(g, 0.001), about=(f.cx, f.top + 1010)):
            text(c, "9.1×", f.cx, f.top + 1010, size=130, color=RED, weight="extrabold", glow=8)
    text(c, "3DCenter price index, Nov 2026 · DDR5 index: 607% of July 2025", f.cx, f.top + 1110,
         size=26, color=GREY, weight="medium", alpha=f.p(("nine", 0.3), 0.5))


# ------------------------------------------------------------------ 3. same wafers
@VIDEO.scene("wafers", lines=[
    Line("Your RAM and AI's memory are cut from the same silicon wafers.",
         show="Your RAM and AI's memory are cut from the same silicon wafers."),
    Line("And memory makers are moving those wafers to AI servers.",
         show="And memory makers are moving those wafers to AI servers."),
], sfx=[("whoosh", 0.0), ("pop", "same"), ("tick", "wafers"), ("whoosh", "moving"),
        ("hit", "servers")])
def wafers(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    a = f.p(0.0, 0.6, "out")
    cx, cy, r = f.cx, f.top + 330, 260
    k = f.p(0.1, 1.6, "out")
    wafer(c, cx, cy, r, 52, BLUE, progress=k, alpha=a)
    s = f.p("same", 0.5)
    text(c, "one wafer", cx, cy + r + 50, size=40, color=WHITE, weight="extrabold", alpha=s)
    # destinations
    m = f.p("moving", 1.2, "smooth")
    yd = f.top + 900
    for x, lab, col, share in ((280, "your PC", GREEN, 1 - 0.55 * m), (800, "AI servers", BLUE, 1.0)):
        rect(c, x - 170, yd, 340, 150, fill=PANEL, stroke=col, width=4, radius=20, alpha=a)
        text(c, lab, x, yd + 75, size=46, color=col, weight="extrabold", alpha=a)
    # arrows: the PC one thins, the server one thickens
    if f.after(0.6):
        arrow(c, cx - 60, cy + r + 90, 300, yd - 20, color=GREEN, width=max(16 * (1 - 0.8 * m), 3),
              progress=f.p(0.6, 0.6), alpha=a)
        arrow(c, cx + 60, cy + r + 90, 780, yd - 20, color=BLUE, width=6 + 18 * m,
              progress=f.p(0.6, 0.6), alpha=a)
    text(c, "TrendForce: capacity shifting to server memory, Q4 2026", f.cx, f.top + 1120, size=26,
         color=GREY, weight="medium", alpha=f.p("servers", 0.5))


# ------------------------------------------------------------------ 4. HBM eats 3x the wafer
@VIDEO.scene("hbm", lines=[
    Line("Worse, AI's memory, H B M, needs about three times the wafer area",
         show="Worse, AI's memory, HBM, needs about 3× the wafer area"),
    Line("for the same capacity, Micron says.", show="for the same capacity, Micron says."),
], sfx=[("whoosh", 0.0), ("pop", "h"), ("hit", "three"), ("ding", "micron")])
def hbm(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    a = f.p(0.0, 0.5, "out")
    r = 210
    y = f.top + 330
    n1 = wafer(c, 290, y, r, 46, GREEN, progress=f.p(0.1, 1.0, "out"), alpha=a, label="DDR5")
    k = f.p("h", 1.2, "out")
    wafer(c, 790, y, r, 46 * math.sqrt(3), BLUE, progress=k, alpha=a, label="HBM")
    # "same capacity": a gigabyte counter under each
    t = f.p("three", 0.6, "overshoot")
    if t > 0:
        with moved(c, scale=max(t, 0.001), about=(f.cx, f.top + 760)):
            runs(c, [("same GB → ", WHITE), ("~3×", RED), (" the silicon", WHITE)], f.cx, f.top + 760,
                 size=64, weight="extrabold")
    # three DDR5 wafers = one wafer's worth of HBM
    s = f.p("same", 0.8, "out")
    if s > 0:
        for i in range(3):
            with moved(c, alpha=clamp(s * 3 - i)):
                circle(c, 300 + i * 120, f.top + 950, 52, fill="#20262F", stroke=BLUE, width=4)
        text(c, "=", 690, f.top + 950, size=80, color=GREY, weight="bold", alpha=s)
        circle(c, 820, f.top + 950, 52, fill="#20262F", stroke=GREEN, width=4, alpha=s)
        text(c, "3 wafers of HBM", 420, f.top + 1040, size=34, color=BLUE, weight="bold", alpha=s)
        text(c, "1 of DDR5", 820, f.top + 1040, size=34, color=GREEN, weight="bold", alpha=s)
    text(c, "Micron, Hot Chips 2026 (via Tom's Hardware, Aug 25) · illustration", f.cx, f.top + 1120,
         size=26, color=GREY, weight="medium", alpha=f.p("micron", 0.5))


# ------------------------------------------------------------------ 5. verdict
@VIDEO.scene("verdict", lines=[
    Line("So every AI server soaks up memory your PC would have used.",
         show="So every AI server soaks up memory your PC would have used."),
    Line("TrendForce expects prices to keep rising, just more slowly.",
         show="TrendForce expects prices to keep rising, just more slowly."),
    Line("This Black Friday, the deal is the RAM you already own.",
         show="This Black Friday, the deal is the RAM you already own."),
], sfx=[("whoosh", 0.0), ("pop", "soaks"), ("tick", "rising"), ("riser", ("deal", -0.6)),
        ("ding", ("own", 0.2))], pad_out=0.7)
def verdict(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    a = f.p(0.0, 0.5)
    # a rising price curve that keeps climbing but flattens
    X0, X1, Y0, Y1 = 140, 960, f.top + 560, f.top + 120
    text(c, "DRAM prices (shape only)", f.cx, f.top + 50, size=38, color=GREY, weight="extrabold", alpha=a)
    line(c, X0, Y0, X1, Y0, color=DIM, width=3, alpha=a)
    pts = []
    for i in range(101):
        u = i / 100
        v = 1 - math.exp(-3.2 * u)
        pts.append((X0 + u * (X1 - X0), Y0 - v * (Y0 - Y1)))
    s = f.p("trendforce", 2.2, "smooth")
    if s > 0:
        stroke_path(c, polyline(pts), color=RED, width=8, progress=s)
        sl = f.p("slowly", 0.5)
        text(c, "still up, more slowly", 760, Y1 - 10, size=34, color=RED, weight="bold", alpha=sl)
    # soak: server box draining a PC box
    k = f.p("soaks", 0.8, "out")
    if k > 0 and not f.after("this"):
        with moved(c, alpha=k * (1 - f.p(("this", -0.4), 0.4))):
            chip(c, 300, f.top + 860, 200, color=BLUE, label="AI")
            arrow(c, 620, f.top + 860, 430, f.top + 860, color=BLUE, width=10, progress=k)
            stick(c, 790, f.top + 860, w=300, h=90, alpha=1 - 0.7 * k)
            text(c, "your PC's share", 790, f.top + 960, size=32, color=GREY, weight="bold")
    d = f.p("deal", 0.6, "out")
    if d > 0:
        y = f.top + 870
        with moved(c, dy=(1 - d) * 80, alpha=d):
            stick(c, f.cx, y, w=700, h=160)
            text(c, "the RAM you already own", f.cx, y + 170, size=58, color=GOLD, weight="extrabold",
                 glow=6 * f.p("own", 0.5))
    text(c, "TrendForce DRAM bulletin, Nov 18, 2026 · prices as of Oct-Nov 2026", f.cx, f.top + 1120,
         size=26, color=GREY, weight="medium", alpha=f.p("trendforce", 0.5))
