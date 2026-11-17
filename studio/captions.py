"""Captions: burnt-in for Shorts (three words at a time, the spoken word in gold) and .srt files."""
from .brand import GOLD, WHITE, BG
from .draw import font, rect, paint
from .ease import clamp, overshoot

BREAK = (".", ",", "?", "!", ";", ":", "—")


def chunks(plan, max_words=3):
    """Caption chunks across the whole video: [(words, start, end)]."""
    out = []
    for sc in plan:
        for pl in sc.lines:
            cur = []
            for w in pl.shown:
                cur.append(w)
                if len(cur) == max_words or w[0].endswith(BREAK):
                    out.append(cur)
                    cur = []
            if cur:
                out.append(cur)
    timed = []
    for i, ws in enumerate(out):
        start, end = ws[0][1], ws[-1][2] + 0.3
        if i + 1 < len(out):  # hand over to the next chunk without a gap or an overlap
            end = max(ws[-1][2], min(end, out[i + 1][0][1]))
        timed.append((ws, start, end))
    return timed


def draw_caption(c, video, cks, T, size=70):
    """Draw the caption chunk active at global time T (Shorts only)."""
    if video.caption_y is None:
        return
    for ws, s, e in cks:
        if s <= T < e:
            break
    else:
        return
    f = font(size, "extrabold")
    space = f.measureText(" ")
    texts = [w for w, _, _ in ws]
    widths = [f.measureText(t) for t in texts]
    total = sum(widths) + space * (len(texts) - 1)
    pop = overshoot(clamp((T - s) / 0.12))
    scale = 0.9 + 0.1 * pop
    cx, cy = video.W / 2, video.caption_y
    c.save()
    c.translate(cx, cy)
    c.scale(scale, scale)
    pad_x, pad_y = 34, 26
    cap = f.getMetrics().fCapHeight
    rect(c, -total / 2 - pad_x, -cap / 2 - pad_y, total + 2 * pad_x, cap + 2 * pad_y,
         fill=BG, radius=22, alpha=0.62)
    x = -total / 2
    for (w, ws_, we), t, wd in zip(ws, texts, widths):
        col = GOLD if ws_ <= T < max(we, ws_ + 0.12) else WHITE
        c.drawString(t, x, cap / 2, f, paint(col))
        x += wd + space
    c.restore()


def _ts(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def srt(plan, max_chars=42):
    """Upload captions: one or two short lines per cue, timed to the words."""
    cues, n = [], 1
    for sc in plan:
        for pl in sc.lines:
            group, length = [], 0
            for w in pl.shown:
                if group and (length + len(w[0]) + 1 > max_chars * 2 or group[-1][0].endswith((".", "?", "!"))):
                    cues.append(group)
                    group, length = [], 0
                group.append(w)
                length += len(w[0]) + 1
            if group:
                cues.append(group)
    out = []
    for g in cues:
        words = [w for w, _, _ in g]
        text, line1 = " ".join(words), []
        if len(text) > max_chars:
            for w in words:
                if len(" ".join(line1 + [w])) > len(text) / 2 and line1:
                    break
                line1.append(w)
            text = " ".join(line1) + "\n" + " ".join(words[len(line1):])
        out.append(f"{n}\n{_ts(g[0][1])} --> {_ts(g[-1][2] + 0.15)}\n{text}\n")
        n += 1
    return "\n".join(out)
