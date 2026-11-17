"""The Thinking Sand studio: vector animation, narration with exact word timings,
captions, synthesized sound and the standard end card, in the channel's style.

    from studio import *
    VIDEO = Video("my-short", format="short", question="Which would you buy?")

    @VIDEO.scene("hook", lines=[Line("Eight and a half times the cores...")])
    def hook(f):
        text(f.c, "8.5×", f.cx, f.cy, size=220, color=GOLD, alpha=f.p("eight"))
"""
from .brand import (BG, GOLD, BLUE, WHITE, GREY, DIM, RED, GREEN, TEAL, PURPLE, SAND,
                    NAME, HANDLE, FPS, FORMATS)
from .ease import (clamp, linear, smooth, ease_in, ease_out, overshoot, there_and_back, pulse,
                   lerp, lerp_color)
from .draw import (text, runs, typewriter, number, measure, wrap, rect, box, circle, line, arrow,
                   brace, grid, bar, blocks, chip, polyline, stroke_path, partial, moved, paint,
                   rgba, font, vignette)
from .logo import draw_logo
from .timeline import Video, Line, Frame

__all__ = [n for n in dir() if not n.startswith("_")]
