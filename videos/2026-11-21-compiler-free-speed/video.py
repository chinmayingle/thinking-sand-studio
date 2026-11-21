"""Short: same CPU, same code, up to 6.5% faster. Only the compiler changed.

Lane: bridge (code told through the hardware the viewer uses).

Facts (see claude/compiler-free-speed-short.md in the CC project):
- ServeTheHome, "The Case For Compilers: A Look at SPEC CPU 2026 on LLVM 22" (Ryan Smith,
  May 10, 2026). LLVM 20.1.8 vs LLVM 22.1.4, Ubuntu 24.04, base rates, "unofficial" estimates.
  Full-system SPECrate int uplift: Intel Core Ultra 9 285HX +4.0%, AMD Ryzen AI Max+ 395 +5.0%,
  Nvidia DGX Spark (GB10, Arm X925/A725) +6.5%. 750.sealcrypto_r +129% on the DGX Spark
  (+63% Intel, +90% AMD). 707.ntest_r -3.1% on AMD. Gains "extremely benchmark-specific".
- Microsoft C++ Team Blog, "C++ Optimizations in MSVC Build Tools 14.52" (Troy Johnson,
  Nov 17, 2026; Visual Studio 2026): on ARM64 a loop's 19 indexed loads become nine ldp
  (load pair) + one ldr; another sequence goes "from 16 instructions to nine". No overall %.
Build: python -m studio.make videos/2026-11-21-compiler-free-speed
"""
from studio import *

VIDEO = Video("compiler-free-speed", format="short", speed=1.08,
              question="Which app on your PC do you wish ran faster?")

CODE = GREEN
INSN = BLUE


def code_card(c, x, y, w, h, alpha=1.0, lines=("for each enemy:", "  move(enemy)", "  hit_test(enemy)")):
    rect(c, x, y, w, h, fill="#141A16", stroke=CODE, width=4, radius=18, alpha=alpha)
    for i, s in enumerate(lines):
        text(c, s, x + 30, y + 60 + i * 56, size=38, color=CODE, weight="medium", align="left", alpha=alpha)


def insn_stack(c, x, y, n, w=200, h=34, gap=10, color=INSN, alpha=1.0, label=None):
    for i in range(n):
        rect(c, x, y + i * (h + gap), w, h, fill=color, radius=6, alpha=alpha * 0.9)
    if label:
        text(c, label, x + w / 2, y - 40, size=34, color=color, weight="bold", alpha=alpha)


# ------------------------------------------------------------------ 1. hook
@VIDEO.scene("hook", lines=[
    Line("Same chip. Same code. Six and a half percent faster.",
         show="Same chip. Same code. 6.5% faster."),
    Line("And nobody touched the hardware."),
], pad_in=0.1, sfx=[("whoosh", 0.0), ("tick", "same"), ("tick", "code"), ("riser", ("six", -0.4)),
                    ("hit", "faster"), ("pop", "nobody")])
def hook(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    a = f.p(0.0, 0.4, "out")
    cy = f.top + 330
    g = f.p("faster", 0.6)
    chip(c, f.cx + 230, cy, 260, color=BLUE, label="CPU", alpha=a, glow=0.8 * g)
    text(c, "same chip", f.cx + 230, cy + 190, size=36, color=GREY, weight="bold", alpha=f.p("chip", 0.4))
    k = f.p("code", 0.5, "out")
    with moved(c, dx=-(1 - k) * 120, alpha=k):
        code_card(c, 60, cy - 120, 430, 240)
        text(c, "same code", 275, cy + 190, size=36, color=GREY, weight="bold")
    n = f.p("six", 1.1, "out")
    if n > 0:
        number(c, lerp(0, 6.5, n), f.cx, f.top + 760, fmt="+{:.1f}%", size=230, color=GOLD)
        text(c, "faster", f.cx, f.top + 900, size=56, color=WHITE, weight="extrabold", alpha=n)
    h = f.p("nobody", 0.5, "overshoot")
    if h > 0:
        with moved(c, scale=max(h, 0.001), about=(f.cx, f.top + 1040)):
            box(c, f.cx, f.top + 1040, 760, 100, fill="#2A1715", stroke=RED, width=4, radius=50)
            text(c, "no new hardware", f.cx, f.top + 1040, size=50, color=RED, weight="extrabold")


# ------------------------------------------------------------------ 2. the compiler
@VIDEO.scene("compiler", lines=[
    Line("The only thing that changed was the compiler."),
    Line("It turns the code people write into instructions your CPU runs."),
], sfx=[("pop", "compiler"), ("whoosh", "turns"), ("ding", "runs")])
def compiler(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    a = f.p(0.0, 0.4)
    y = f.top + 120
    code_card(c, 70, y, 430, 240, alpha=a)
    text(c, "what people write", 285, y - 40, size=34, color=CODE, weight="bold", alpha=a)
    k = f.p("compiler", 0.5, "overshoot")
    if k > 0:
        with moved(c, scale=max(k, 0.001), about=(f.cx, f.top + 520)):
            box(c, f.cx, f.top + 520, 420, 130, fill="#2A2613", stroke=GOLD, width=5, radius=20)
            text(c, "COMPILER", f.cx, f.top + 520, size=62, color=GOLD, weight="extrabold")
    t = f.p("turns", 0.9)
    arrow(c, 285, y + 260, f.cx - 120, f.top + 450, color=CODE, width=5, progress=t)
    # instructions fall out the bottom into the chip
    r = f.p(("instructions", -0.1), 1.2, "linear")
    n = int(round(12 * r))
    for i in range(n):
        rect(c, 160 + (i % 6) * 130, f.top + 650 + (i // 6) * 54, 112, 40, fill=INSN, radius=6, alpha=0.9)
    if n:
        text(c, "instructions", 160, f.top + 625, size=34, color=INSN, weight="bold", align="left", alpha=r)
    g = f.p("runs", 0.5, "out")
    if g > 0:
        arrow(c, f.cx, f.top + 780, f.cx, f.top + 880, color=INSN, width=5, progress=g)
        chip(c, f.cx, f.top + 990, 170, color=BLUE, label="CPU", alpha=g, glow=0.6)


# ------------------------------------------------------------------ 3. load pairs
PAIR_TOP = 360


@VIDEO.scene("pairs", lines=[
    Line("This week, Microsoft's compiler learned to turn nineteen loads into ten,",
         show="This week, Microsoft's compiler learned to turn 19 loads into 10,"),
    Line("by grabbing two values at once."),
    Line("Fewer instructions, same result."),
], sfx=[("whoosh", 0.0), ("tick", "nineteen"), ("riser", ("ten", -0.5)), ("pop", "two"), ("ding", "fewer")])
def pairs(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    a = f.p(0.0, 0.4)
    text(c, "Microsoft C++ compiler 14.52 · Arm laptops", f.cx, f.top + 30, size=34, color=GREY,
         weight="medium", alpha=a)
    m = f.p("two", 1.0, "smooth")      # merge progress
    shown = f.p(("nineteen", -0.2), 0.9, "linear")
    n_vis = int(round(19 * shown))
    top = f.top + PAIR_TOP - 150
    h, gap = 40, 8
    # 19 single loads in two columns -> 9 pairs + 1 in one wide column
    for i in range(n_vis):
        pair, side = divmod(i, 2)
        # before: column layout, 10 rows, two columns
        bx = 180 + (i // 10) * 300
        by = top + (i % 10) * (h + gap)
        # after: pair row, the two halves side by side
        ax = 560 + side * 170
        ay = top + pair * (h + gap)
        x = lerp(bx, ax, m)
        y = lerp(by, ay, m)
        col = lerp_color(INSN, GOLD, m) if i < 18 else INSN
        rect(c, x, y, 160, h, fill=col, radius=6, alpha=0.92)
        text(c, "load", x + 80, y + h / 2, size=26, color=BG, weight="extrabold")
    if m > 0.6:
        for p in range(9):
            y = top + p * (h + gap)
            rect(c, 552, y - 4, 346, h + 8, stroke=GOLD, width=3, radius=8, alpha=(m - 0.6) / 0.4)
    # counter
    cnt = 19 if m < 0.5 else 10
    if n_vis:
        number(c, cnt if shown >= 1 else n_vis, 330 if m < 0.5 else 300, f.top + 830,
               fmt="{:.0f}", size=170, color=GOLD if m >= 0.5 else INSN)
        text(c, "instructions", 330 if m < 0.5 else 300, f.top + 940, size=40, color=GREY, weight="bold")
    if m >= 0.5:
        text(c, "load two at once", 730, f.top + 830, size=40, color=GOLD, weight="extrabold", alpha=(m - 0.5) * 2)
    q = f.p("fewer", 0.5, "overshoot")
    if q > 0:
        with moved(c, scale=max(q, 0.001), about=(f.cx, f.top + 1060)):
            text(c, "less work, same answer", f.cx, f.top + 1060, size=60, color=WHITE, weight="extrabold")


# ------------------------------------------------------------------ 4. the benchmark
@VIDEO.scene("bench", lines=[
    Line("Testers rebuilt a standard CPU benchmark with a newer compiler."),
    Line("Intel: four percent faster. AMD: five. Nvidia's Arm chip: six and a half.",
         show="Intel: 4% faster. AMD: 5%. Nvidia's Arm chip: 6.5%."),
], sfx=[("whoosh", 0.0), ("pop", "intel"), ("pop", "five"), ("hit", ("six", 0.2))])
def bench(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    a = f.p(0.0, 0.4)
    text(c, "SPEC CPU 2026 · LLVM 22 vs LLVM 20", f.cx, f.top + 30, size=40, color=WHITE,
         weight="extrabold", alpha=a)
    text(c, "same chips, only the compiler changed", f.cx, f.top + 90, size=34, color=GREY,
         weight="medium", alpha=f.p("rebuilt", 0.5))
    base = f.top + 820
    items = [("intel", "Intel", "Core Ultra 9\n285HX", 4.0),
             ("five", "AMD", "Ryzen AI\nMax+ 395", 5.0),
             (("six", -0.1), "Nvidia", "GB10\n(DGX Spark)", 6.5)]
    for i, (cue, name, model, v) in enumerate(items):
        k = f.p(cue, 0.8, "out")
        x = 230 + i * 310
        bar(c, x, base, 190, 80 * v, color=GOLD if i == 2 else BLUE, progress=k)
        if k > 0:
            text(c, f"+{v * clamp(k):.1f}%", x, base - 80 * v * k - 50, size=60,
                 color=GOLD if i == 2 else WHITE, weight="extrabold", alpha=clamp(k * 2))
            text(c, name, x, base + 50, size=44, color=WHITE, weight="extrabold", alpha=k)
            for j, s in enumerate(model.split("\n")):
                text(c, s, x, base + 100 + j * 38, size=30, color=GREY, weight="medium", alpha=k)
    text(c, "ServeTheHome, May 2026 · unofficial estimates", f.cx, f.top + 1070, size=30, color=GREY,
         weight="medium", alpha=f.p("intel", 0.5))


# ------------------------------------------------------------------ 5. uneven
@VIDEO.scene("uneven", lines=[
    Line("But it's uneven. One encryption test more than doubled. Another got three percent slower.",
         show="But it's uneven. One encryption test more than doubled. Another got 3% slower."),
], sfx=[("tick", "uneven"), ("riser", ("doubled", -0.6)), ("hit", "doubled"), ("pop", "slower")])
def uneven(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    base = f.top + 760
    line(c, 120, base, 960, base, color=GREY, width=3, alpha=f.p(0.0, 0.4))
    text(c, "old compiler = 0", 960, base - 30, size=30, color=GREY, weight="medium", align="right",
         alpha=f.p(0.0, 0.4))
    k = f.p(("doubled", -0.5), 1.0, "overshoot")
    if k > 0:
        hgt = 4.4 * 129 * k
        rect(c, 230, base - hgt, 200, hgt, fill=GREEN, radius=8)
        text(c, f"+{129 * clamp(k):.0f}%", 330, base - hgt - 60, size=72, color=GREEN, weight="extrabold", glow=6)
        text(c, "encryption test", 330, base + 50, size=36, color=WHITE, weight="bold")
        text(c, "Nvidia GB10", 330, base + 95, size=30, color=GREY, weight="medium")
    s = f.p("slower", 0.6, "out")
    if s > 0:
        hgt = 14 * 3.1 * s
        rect(c, 600, base, 200, hgt, fill=RED, radius=8)
        text(c, "-3%", 905, base + 40, size=72, color=RED, weight="extrabold", alpha=s)
        text(c, "board-game AI test", 700, base + 120, size=36, color=WHITE, weight="bold", alpha=s)
        text(c, "AMD", 700, base + 165, size=30, color=GREY, weight="medium", alpha=s)


# ------------------------------------------------------------------ 6. why it matters to you
APPS = [("game", GOLD), ("browser", BLUE), ("editor", GREEN), ("video app", PURPLE)]


@VIDEO.scene("you", lines=[
    Line("Every app and game on your PC went through a compiler."),
    Line("When developers rebuild with a newer one, you get the speed for free."),
], sfx=[("pop", "app"), ("pop", "game"), ("whoosh", "rebuild"), ("ding", "free")], pad_out=0.4)
def you(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    for i, (name, col) in enumerate(APPS):
        k = f.p(("every", 0.25 * i), 0.4, "overshoot")
        if k > 0:
            x = 170 + i * 247
            with moved(c, scale=max(k, 0.001), about=(x, f.top + 120)):
                box(c, x, f.top + 120, 210, 110, fill="#161B23", stroke=col, width=4, radius=20)
                text(c, name, x, f.top + 120, size=36, color=col, weight="bold")
    a = f.p("compiler", 0.5, "overshoot")
    if a > 0:
        with moved(c, scale=max(a, 0.001), about=(f.cx, f.top + 420)):
            box(c, f.cx, f.top + 420, 560, 120, fill="#2A2613", stroke=GOLD, width=5, radius=20)
            text(c, "NEWER COMPILER" if f.after("rebuild") else "COMPILER", f.cx, f.top + 420, size=54,
                 color=GOLD, weight="extrabold")
        for i in range(4):
            arrow(c, 170 + i * 247, f.top + 190, f.cx + (i - 1.5) * 90, f.top + 350, color=GREY, width=3,
                  head=14, progress=a, alpha=0.6)
    r = f.p("rebuild", 0.8)
    if r > 0:
        arrow(c, f.cx, f.top + 490, f.cx, f.top + 640, color=GOLD, width=6, progress=r)
    g = f.p("free", 0.6, "out")
    chip(c, f.cx, f.top + 780, 220, color=BLUE, label="CPU", alpha=clamp(r * 2), glow=1.2 * g)
    if g > 0:
        with moved(c, scale=max(f.p("free", 0.5, "overshoot"), 0.001), about=(f.cx, f.top + 1010)):
            text(c, "same hardware, free speed", f.cx, f.top + 1010, size=58, color=GOLD, weight="extrabold",
                 glow=6)
