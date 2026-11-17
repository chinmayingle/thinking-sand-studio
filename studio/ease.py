"""Easing and interpolation. Everything takes and returns plain floats."""
import math


def clamp(x, lo=0.0, hi=1.0):
    return lo if x < lo else hi if x > hi else x


def linear(x):
    return clamp(x)


def smooth(x):
    """Smootherstep: the soft start and stop of a 3Blue1Brown move."""
    x = clamp(x)
    return x * x * x * (x * (6 * x - 15) + 10)


def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_in(x):
    x = clamp(x)
    return x ** 3


def overshoot(x):
    """Pops slightly past 1 and settles: good for things that land."""
    x = clamp(x)
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def there_and_back(x):
    x = clamp(x)
    return smooth(2 * x) if x < 0.5 else smooth(2 - 2 * x)


def pulse(t, period=1.2):
    """0..1..0 breathing loop for glows."""
    return 0.5 - 0.5 * math.cos(2 * math.pi * t / period)


EASES = {
    "linear": linear,
    "smooth": smooth,
    "out": ease_out,
    "in": ease_in,
    "overshoot": overshoot,
    "there_and_back": there_and_back,
}


def lerp(a, b, p):
    return a + (b - a) * p


def hex_rgb(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def lerp_color(c1, c2, p):
    a, b = hex_rgb(c1), hex_rgb(c2)
    r = [round(lerp(a[i], b[i], clamp(p))) for i in range(3)]
    return "#%02X%02X%02X" % tuple(r)
