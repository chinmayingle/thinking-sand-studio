"""The etched-grain mark (logo option A), drawn as vectors so it is sharp at any size.

Geometry copied from the logo design canvas (claude.ai artifact "The Thinking Sand — logo",
project/Main.dc.html and project/Watermark.dc.html), in its 800 x 800 units.
"""
import skia

from .brand import BG, GOLD, BLUE
from .draw import paint, partial, polyline, rgba
from .ease import clamp, smooth, overshoot

GRAIN = [(392, 128), (505, 118, 622, 178, 655, 290), (690, 402, 660, 528, 568, 610),
         (488, 680, 362, 690, 268, 642), (168, 590, 118, 482, 136, 372),
         (152, 262, 262, 138, 392, 128)]
TRACES = [
    [(372, 340), (372, 262), (330, 220)],
    [(428, 340), (428, 215)],
    [(465, 375), (560, 375), (600, 335)],
    [(465, 435), (555, 435), (598, 478)],
    [(400, 470), (400, 590)],
    [(360, 470), (360, 520), (300, 580)],
    [(335, 405), (215, 405)],
    [(335, 360), (285, 360), (245, 320)],
]
# The watermark keeps five traces, drawn bolder (30 instead of 22, pads 28 instead of 22).
WATERMARK_TRACES = [0, 2, 3, 5, 6]
SPECKS = [(690, 560, 10, 0.6), (712, 470, 6, 0.4), (110, 250, 8, 0.5), (160, 640, 6, 0.35), (585, 100, 7, 0.45)]


def _grain_path():
    p = skia.Path()
    p.moveTo(*GRAIN[0])
    for seg in GRAIN[1:]:
        p.cubicTo(*seg)
    p.close()
    return p


def draw_logo(c, cx, cy, size, progress=1.0, bg=BG, watermark=False, specks=True, glow=0.0):
    """Draw the mark centred on (cx, cy), `size` pixels across (the 800-unit artboard).

    progress animates it in: the grain lands (0-0.3), traces etch in (0.25-0.75),
    pads appear (0.6-0.85), the core lights up (0.75-1). glow (0..1) adds a soft
    halo to the blue core, e.g. glow=ease.pulse(t) for a breathing end card.
    """
    p = clamp(progress)
    c.save()
    c.translate(cx, cy)
    if watermark:  # 300-unit artboard: translate(150 150) scale(0.47) translate(-401 -404)
        s = size / 300.0 * 0.47
        c.scale(s, s)
        c.translate(-401, -404)
    else:          # 800-unit artboard, centred
        s = size / 800.0
        c.scale(s, s)
        c.translate(-400, -400)

    if specks and not watermark:
        for (x, y, r, a) in SPECKS:
            c.drawCircle(x, y, r, paint(GOLD, a * clamp(p * 3)))

    land = overshoot(clamp(p / 0.3))
    c.save()
    c.translate(401, 404)
    c.scale(max(land, 0.001), max(land, 0.001))
    c.translate(-401, -404)
    c.drawPath(_grain_path(), paint(GOLD, clamp(p / 0.15)))
    c.restore()

    traces = [TRACES[i] for i in WATERMARK_TRACES] if watermark else TRACES
    tw, pr = (30, 28) if watermark else (22, 22)
    etch = smooth(clamp((p - 0.25) / 0.5))
    for pts in traces:
        c.drawPath(partial(polyline(pts), etch), paint(bg, 1, stroke=True, width=tw))
    pads = overshoot(clamp((p - 0.6) / 0.25))
    for pts in traces:
        x, y = pts[-1]
        if pads > 0:
            c.drawCircle(x, y, pr * pads, paint(bg))

    core = smooth(clamp((p - 0.75) / 0.25))
    if watermark:
        outer, inner = (325, 330, 150, 150, 22), (355, 360, 90, 90, 12)
    else:
        outer, inner = (335, 340, 130, 130, 18), (362, 367, 76, 76, 10)
    if core > 0:
        x, y, w, h, r = outer
        c.drawRoundRect(skia.Rect.MakeXYWH(x, y, w, h), r, r, paint(bg))
        x, y, w, h, r = inner
        if glow > 0:
            c.drawRoundRect(skia.Rect.MakeXYWH(x - 12, y - 12, w + 24, h + 24), r + 8, r + 8,
                            paint(BLUE, 0.7 * glow * core, blur=22))
        c.drawRoundRect(skia.Rect.MakeXYWH(x, y, w, h), r, r, paint(BLUE, core))
    c.restore()


def export_pngs(out_dir):
    """Write the profile picture (800 x 800, dark background) and the watermark (300 x 300, transparent)."""
    import numpy as np
    from pathlib import Path
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    buf = np.zeros((800, 800, 4), np.uint8)
    surf = skia.Surface(buf)
    cv = surf.getCanvas()
    cv.clear(rgba(BG))
    draw_logo(cv, 400, 400, 800)
    surf.makeImageSnapshot().save(str(out_dir / "logo-800.png"), skia.kPNG)

    buf = np.zeros((300, 300, 4), np.uint8)
    surf = skia.Surface(buf)
    cv = surf.getCanvas()
    cv.clear(skia.Color(0, 0, 0, 0))
    draw_logo(cv, 150, 150, 300, watermark=True, specks=False)
    surf.makeImageSnapshot().save(str(out_dir / "watermark-300.png"), skia.kPNG)
