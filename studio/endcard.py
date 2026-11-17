"""The standard ending: the comment question, then like/share/subscribe, then the mark,
"The Thinking Sand" and @TheThinkingSand (video-rules.md, "Ending")."""
from .brand import GOLD, BLUE, WHITE, GREY, RED, NAME, HANDLE
from .draw import text, box, moved
from .ease import smooth, overshoot, pulse, clamp
from .logo import draw_logo
from .timeline import Line, SceneDef


def endcard_scene(video):
    q = video.question or "What should I explain next?"
    lines = video.endcard_lines or [
        Line(f"{q} Tell me in the comments."),
        Line("And if this helped, like, share, and subscribe to The Thinking Sand.",
             show="If this helped: like, share, and subscribe to The Thinking Sand."),
    ]

    def draw(f):
        c, W = f.c, f.W
        short = video.format == "short"

        def when(word, default):
            try:
                return f.cue(word)
            except KeyError:
                return default

        q_y = f.top + (150 if short else 170)
        row_y = q_y + (330 if short else 255)
        logo_size = 400 if short else 300
        logo_y = row_y + (330 if short else 250)

        # 1. the question, large, in gold
        a = f.p(0.0, 0.5)
        with moved(c, dy=(1 - a) * 30, alpha=a):
            text(c, q, W / 2, q_y, size=74 if short else 64, color=GOLD, weight="bold",
                 max_width=W * (0.84 if short else 0.7))
        c_at = when("comments", 1.0) - 0.4
        text(c, "Tell me in the comments", W / 2, q_y + (170 if short else 120), size=44, color=GREY,
             weight="medium", alpha=f.p(c_at, 0.4))

        # 2. like / share / subscribe light up as they are said
        end1 = f.line_end(0) if f.scene.lines else 1.0
        k = f.p(end1, 0.45, "out")
        xs = [W / 2 - 300, W / 2 - 60, W / 2 + 230] if short else [W / 2 - 330, W / 2 - 90, W / 2 + 200]
        for (lab, word), x in zip([("LIKE", "like"), ("SHARE", "share"), ("SUBSCRIBE", "subscribe")], xs):
            at = when(word, end1 + 0.5)
            on = f.t >= at
            pop = overshoot(f.p(at, 0.3))
            with moved(c, scale=0.92 + 0.08 * pop, about=(x, row_y), alpha=k):
                if lab == "SUBSCRIBE":
                    box(c, x, row_y, 330, 92, fill=RED if on else "#3A1F22", radius=46)
                    text(c, lab, x, row_y, size=40, color=WHITE, weight="extrabold")
                else:
                    box(c, x, row_y, 200, 92, stroke=GOLD if on else GREY, width=4, radius=46)
                    text(c, lab, x, row_y, size=38, color=GOLD if on else GREY, weight="bold")

        # 3. the mark etches itself in, then the name and the handle
        logo_t = when("subscribe", end1 + 0.8) + 0.3
        lp = clamp((f.t - logo_t) / 1.4)
        if lp > 0:
            draw_logo(c, W / 2, logo_y, logo_size, progress=lp, glow=pulse(f.t, 1.6) * smooth(lp))
            n = f.p(logo_t + 0.9, 0.5)
            with moved(c, dy=(1 - n) * 20, alpha=n):
                text(c, NAME, W / 2, logo_y + logo_size * 0.62, size=64, color=WHITE, weight="bold")
                text(c, HANDLE, W / 2, logo_y + logo_size * 0.62 + 78, size=44, color=BLUE, weight="semibold")

    return SceneDef("endcard", draw, lines, pad_in=0.2, pad_out=2.2, fade=True, captions=False,
                    sfx=[("pop", "like"), ("pop", "share"), ("ding", "subscribe"), ("swell", ("subscribe", 0.3))])
