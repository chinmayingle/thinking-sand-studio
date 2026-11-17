"""Skia drawing helpers in the channel's style.

Every helper takes the canvas first. Colours are hex strings. `alpha` multiplies
the colour's opacity. Anything with `progress` draws partially (0..1), which is
how strokes "write on" the way they do in 3Blue1Brown videos.
"""
from contextlib import contextmanager
from functools import lru_cache
import math

import skia

from .brand import FONTS, BG, WHITE, GOLD, BLUE, GREY, DIM
from .ease import hex_rgb, clamp

FONT_FILES = {
    "regular": "Inter-Regular.ttf",
    "medium": "Inter-Medium.ttf",
    "semibold": "Inter-SemiBold.ttf",
    "bold": "Inter-Bold.ttf",
    "extrabold": "Inter-ExtraBold.ttf",
    "italic": "Inter-Italic.ttf",
    # KaTeX fonts give formulas the Computer Modern look of a maths video.
    "math": "KaTeX_Main-Regular.ttf",
    "math-bold": "KaTeX_Main-Bold.ttf",
    "math-italic": "KaTeX_Math-Italic.ttf",
}


def rgba(color, alpha=1.0):
    r, g, b = hex_rgb(color)
    return skia.Color(r, g, b, int(255 * clamp(alpha)))


@lru_cache(maxsize=None)
def typeface(weight="semibold"):
    tf = skia.Typeface.MakeFromFile(str(FONTS / FONT_FILES[weight]))
    if tf is None:
        raise FileNotFoundError(f"font for weight {weight!r} missing in {FONTS}")
    return tf


@lru_cache(maxsize=512)
def font(size, weight="semibold"):
    f = skia.Font(typeface(weight), size)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    f.setSubpixel(True)
    return f


def paint(color=WHITE, alpha=1.0, stroke=None, width=4.0, blur=0.0):
    p = skia.Paint(AntiAlias=True, Color=rgba(color, alpha))
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(width)
        p.setStrokeCap(skia.Paint.kRound_Cap)
        p.setStrokeJoin(skia.Paint.kRound_Join)
    if blur > 0:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    return p


# ---------------------------------------------------------------- transforms

@contextmanager
def moved(c, dx=0.0, dy=0.0, scale=1.0, rotate=0.0, about=None, alpha=1.0):
    """Translate/scale/rotate (about a point) and fade everything drawn inside."""
    c.save()
    if alpha < 1.0:
        c.saveLayerAlpha(None, int(255 * clamp(alpha)))
    c.translate(dx, dy)
    if about is not None:
        c.translate(*about)
    if rotate:
        c.rotate(rotate)
    if scale != 1.0:
        c.scale(scale, scale)
    if about is not None:
        c.translate(-about[0], -about[1])
    yield c
    if alpha < 1.0:
        c.restore()
    c.restore()


# ---------------------------------------------------------------- text

def measure(s, size=48, weight="semibold"):
    return font(size, weight).measureText(s)


def wrap(s, size, weight, max_width):
    words, lines, cur = s.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if cur and measure(trial, size, weight) > max_width:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def text(c, s, x, y, size=48, color=WHITE, weight="semibold", align="center",
         anchor="middle", alpha=1.0, max_width=None, line_height=1.22, glow=0.0):
    """Draw text. anchor: 'middle' centres the cap height on y; 'baseline' uses y as the baseline.
    A max_width wraps onto several lines centred on y. Returns the block's (width, height)."""
    f = font(size, weight)
    lines = wrap(s, size, weight, max_width) if max_width else s.split("\n")
    m = f.getMetrics()
    cap = m.fCapHeight or size * 0.7
    step = size * line_height
    total = step * (len(lines) - 1)
    y0 = y + cap / 2 - total / 2 if anchor == "middle" else y
    widest = 0
    for i, ln in enumerate(lines):
        w = f.measureText(ln)
        widest = max(widest, w)
        xx = x - w / 2 if align == "center" else x - w if align == "right" else x
        yy = y0 + i * step
        if glow > 0:
            c.drawString(ln, xx, yy, f, paint(color, alpha * 0.6, blur=glow))
        c.drawString(ln, xx, yy, f, paint(color, alpha))
    return widest, total + cap


def runs(c, parts, x, y, size=48, weight="semibold", align="center", alpha=1.0, anchor="middle"):
    """One line made of coloured runs: runs(c, [("Only ", WHITE), ("8 GB", GOLD)], x, y)."""
    f = font(size, weight)
    widths = [f.measureText(s) for s, _ in parts]
    total = sum(widths)
    xx = x - total / 2 if align == "center" else x - total if align == "right" else x
    cap = f.getMetrics().fCapHeight or size * 0.7
    yy = y + cap / 2 if anchor == "middle" else y
    for (s, col), w in zip(parts, widths):
        c.drawString(s, xx, yy, f, paint(col, alpha))
        xx += w
    return total


def typewriter(s, p):
    """The first part of s, for text that types itself in as p goes 0..1."""
    n = round(len(s) * clamp(p))
    return s[:n]


def number(c, value, x, y, fmt="{:,.0f}", size=120, color=GOLD, weight="bold", **kw):
    """A number, e.g. a counter: number(c, lerp(0, 21760, f.p(1.0)), x, y)."""
    return text(c, fmt.format(value), x, y, size=size, color=color, weight=weight, **kw)


# ---------------------------------------------------------------- shapes

def rect(c, x, y, w, h, fill=None, stroke=None, width=4.0, radius=0.0, alpha=1.0, blur=0.0):
    r = skia.Rect.MakeXYWH(x, y, w, h)
    if fill:
        c.drawRoundRect(r, radius, radius, paint(fill, alpha, blur=blur))
    if stroke:
        c.drawRoundRect(r, radius, radius, paint(stroke, alpha, stroke=True, width=width))


def box(c, cx, cy, w, h, **kw):
    """rect() centred on (cx, cy)."""
    rect(c, cx - w / 2, cy - h / 2, w, h, **kw)


def circle(c, x, y, r, fill=None, stroke=None, width=4.0, alpha=1.0, blur=0.0):
    if fill:
        c.drawCircle(x, y, r, paint(fill, alpha, blur=blur))
    if stroke:
        c.drawCircle(x, y, r, paint(stroke, alpha, stroke=True, width=width))


def partial(path, p):
    """The first fraction p of a path's length (across all its contours)."""
    p = clamp(p)
    if p >= 1.0:
        return path
    out = skia.Path()
    if p <= 0.0:
        return out
    lengths, pm = [], skia.PathMeasure(path, False)
    while True:
        lengths.append(pm.getLength())
        if not pm.nextContour():
            break
    target = sum(lengths) * p
    pm = skia.PathMeasure(path, False)
    for L in lengths:
        take = min(L, target)
        if take > 0:
            pm.getSegment(0, take, out, True)
        target -= take
        if target <= 0 or not pm.nextContour():
            break
    return out


def polyline(pts, closed=False):
    path = skia.Path()
    path.moveTo(*pts[0])
    for pt in pts[1:]:
        path.lineTo(*pt)
    if closed:
        path.close()
    return path


def stroke_path(c, path, color=WHITE, width=5.0, progress=1.0, alpha=1.0, blur=0.0):
    c.drawPath(partial(path, progress), paint(color, alpha, stroke=True, width=width, blur=blur))


def line(c, x1, y1, x2, y2, color=WHITE, width=5.0, progress=1.0, alpha=1.0):
    p = clamp(progress)
    if p <= 0:
        return
    c.drawLine(x1, y1, x1 + (x2 - x1) * p, y1 + (y2 - y1) * p,
               paint(color, alpha, stroke=True, width=width))


def arrow(c, x1, y1, x2, y2, color=WHITE, width=6.0, head=24.0, progress=1.0, alpha=1.0):
    """A straight arrow that grows from (x1, y1) as progress goes 0..1."""
    p = clamp(progress)
    if p <= 0:
        return
    ex, ey = x1 + (x2 - x1) * p, y1 + (y2 - y1) * p
    ang = math.atan2(ey - y1, ex - x1)
    bx, by = ex - head * 0.8 * math.cos(ang), ey - head * 0.8 * math.sin(ang)
    c.drawLine(x1, y1, bx, by, paint(color, alpha, stroke=True, width=width))
    tri = polyline([
        (ex, ey),
        (ex - head * math.cos(ang - 0.42), ey - head * math.sin(ang - 0.42)),
        (ex - head * math.cos(ang + 0.42), ey - head * math.sin(ang + 0.42)),
    ], closed=True)
    c.drawPath(tri, paint(color, alpha))


def brace(c, x1, x2, y, label=None, color=GREY, size=40, progress=1.0, alpha=1.0, up=False):
    """A curly brace under (or over, with up=True) the span x1..x2, with a label."""
    d = -1 if up else 1
    h = 26 * d
    mid = (x1 + x2) / 2
    path = skia.Path()
    path.moveTo(x1, y)
    path.cubicTo(x1, y + h, mid - 10, y, mid, y + h * 1.4)
    path.moveTo(x2, y)
    path.cubicTo(x2, y + h, mid + 10, y, mid, y + h * 1.4)
    stroke_path(c, path, color, 4, progress, alpha)
    if label and progress > 0.5:
        text(c, label, mid, y + h * 1.4 + d * (size * 0.9), size=size, color=color,
             alpha=alpha * clamp((progress - 0.5) * 2))


def grid(c, W, H, step=90, color=BLUE, alpha=0.08, top=0, bottom=None):
    """Faint background grid, like a manim NumberPlane."""
    bottom = H if bottom is None else bottom
    p = paint(color, alpha, stroke=True, width=1.5)
    x = (W % step) / 2
    while x <= W:
        c.drawLine(x, top, x, bottom, p)
        x += step
    y = top
    while y <= bottom:
        c.drawLine(0, y, W, y, p)
        y += step


def bar(c, x, base_y, w, h, color=BLUE, progress=1.0, alpha=1.0, label=None, value=None,
        label_size=38, value_size=48, value_color=WHITE, radius=10):
    """A vertical bar growing up from base_y, with a label under it and a value on top."""
    hh = h * clamp(progress)
    if hh > 0:
        rect(c, x - w / 2, base_y - hh, w, hh, fill=color, radius=radius, alpha=alpha)
    if label:
        text(c, label, x, base_y + label_size * 1.1, size=label_size, color=GREY, alpha=alpha)
    if value and progress > 0.05:
        text(c, value, x, base_y - hh - value_size * 0.8, size=value_size, color=value_color,
             weight="bold", alpha=alpha * clamp(progress * 2))


def blocks(c, x, y, n, filled, cols=8, size=46, gap=10, on=GOLD, off=DIM, progress=1.0, alpha=1.0):
    """A grid of n small squares, the first `filled` lit: memory chips, cores, slots."""
    lit = filled * clamp(progress)
    for i in range(n):
        r, k = divmod(i, cols)
        col = on if i < lit else off
        rect(c, x + k * (size + gap), y + r * (size + gap), size, size, fill=col, radius=6, alpha=alpha)


def chip(c, cx, cy, size=260, color=BLUE, label=None, label_color=BG, pins=6, alpha=1.0, glow=0.0):
    """A processor drawn as a die with pins on four sides."""
    s = size
    pin_len, pin_w = s * 0.12, s * 0.05
    for i in range(pins):
        off = -s * 0.36 + i * (s * 0.72 / (pins - 1))
        for (x, y, w, h) in (
            (cx + off - pin_w / 2, cy - s / 2 - pin_len, pin_w, pin_len),
            (cx + off - pin_w / 2, cy + s / 2, pin_w, pin_len),
            (cx - s / 2 - pin_len, cy + off - pin_w / 2, pin_len, pin_w),
            (cx + s / 2, cy + off - pin_w / 2, pin_len, pin_w),
        ):
            rect(c, x, y, w, h, fill=GREY, radius=2, alpha=alpha)
    if glow > 0:
        box(c, cx, cy, s, s, fill=color, radius=s * 0.08, alpha=alpha * 0.55 * glow, blur=s * 0.12)
    box(c, cx, cy, s, s, fill=color, radius=s * 0.08, alpha=alpha)
    box(c, cx, cy, s * 0.62, s * 0.62, stroke=BG, width=s * 0.025, radius=s * 0.05, alpha=alpha * 0.5)
    if label:
        text(c, label, cx, cy, size=s * 0.2, color=label_color, weight="bold", alpha=alpha)


def background(c, W, H, color=BG):
    c.clear(rgba(color))


def vignette(c, W, H, strength=0.55):
    """Darkens the corners slightly so the eye stays in the middle."""
    shader = skia.GradientShader.MakeRadial(
        (W / 2, H / 2), max(W, H) * 0.75,
        [rgba(BG, 0.0), rgba("#000000", strength)], [0.55, 1.0])
    p = skia.Paint(Shader=shader)
    c.drawRect(skia.Rect.MakeWH(W, H), p)
