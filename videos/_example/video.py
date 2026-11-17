"""Example Short: a template and the end-to-end test of the studio. Not for upload.

Copy this folder to videos/<YYYY-MM-DD>-<slug>/ and rewrite it for a real video.
Build: python -m studio.make videos/_example
"""
import math

from studio import *

VIDEO = Video("example", format="short",
              question="Would you pay for more cores, or for faster memory?")


@VIDEO.scene("hook", lines=[
    Line("This chip has eight and a half times the cores of that one.",
         show="This chip has 8.5× the cores of that one."),
    Line("So it should be eight and a half times faster. Right?",
         show="So it should be 8.5× faster. Right?"),
], sfx=[("whoosh", 0.0), ("pop", "this"), ("riser", ("half", -0.8)), ("hit", ("faster", 0.1))])
def hook(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    # two chips land one after the other
    a = f.p("this", 0.5, "overshoot")
    b = f.p("that", 0.5, "overshoot")
    with moved(c, scale=max(a, 0.001), about=(330, f.cy - 120)):
        chip(c, 330, f.cy - 120, 300, color=BLUE, label="B", glow=pulse(f.t))
    with moved(c, scale=max(b, 0.001), about=(800, f.cy - 120)):
        chip(c, 800, f.cy - 120, 140, color=GREY, label="A")
    # the ratio counts up in gold as it is said
    k = f.p("eight", 1.2, "out")
    if k > 0:
        number(c, lerp(1, 8.5, k), f.cx, f.cy + 230, fmt="{:.1f}×", size=200, alpha=min(1, k * 3))
        text(c, "the cores", f.cx, f.cy + 360, size=54, color=GREY, alpha=k)
    # ...so 8.5x the speed?
    q = f.p("faster", 0.5, "overshoot")
    if q > 0:
        runs(c, [("8.5× ", GOLD), ("faster?", WHITE)], f.cx, f.top + 140, size=84, weight="bold", alpha=q)


@VIDEO.scene("why", lines=[
    Line("Not quite. Every core waits on the same memory."),
    Line("When memory can't keep up, extra cores just wait in line."),
], sfx=[("pop", "memory"), ("tick", "wait")])
def why(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    mem_y, core_y = f.top + 170, f.cy + 180
    m = f.p("same", 0.6)
    box(c, f.cx, mem_y, 640 * m + 1, 150, fill=GOLD, radius=18, alpha=m)
    text(c, "MEMORY", f.cx, mem_y, size=60, color=BG, weight="extrabold", alpha=m)
    # one shared road from memory to the cores
    bus = f.p("memory", 0.8)
    arrow(c, f.cx, mem_y + 90, f.cx, core_y - 250, color=WHITE, width=10, progress=bus)
    # data packets moving down the road
    if bus >= 1:
        for i in range(4):
            y = mem_y + 100 + ((f.since("memory") * 220 + i * 90) % 300)
            circle(c, f.cx, y, 14, fill=GOLD)
    # 24 cores: lit while fed, dimmed when they are waiting
    waiting = f.p("wait", 0.8)
    for i in range(24):
        r, k = divmod(i, 6)
        x, y = f.cx - 5 * 75 / 2 + k * 75, core_y - 160 + r * 75
        fed = i < 24 - 18 * waiting
        rect(c, x - 30, y - 30, 60, 60, fill=BLUE if fed else DIM, radius=8, alpha=f.p(0.0, 0.5))
    if waiting > 0:
        text(c, "waiting…", f.cx, core_y + 220, size=64, color=RED, weight="bold", alpha=waiting)
