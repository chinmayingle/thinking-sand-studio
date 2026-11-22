"""Short: your GPU driver was quietly writing up to 30 GB an hour to your SSD.

Lane: proven (hardware: GPU + SSD), with a driver angle.

Facts (see claude/driver-ssd-writes-short.md in the CC project). All write rates are USER
measurements, not Nvidia figures:
- Windows Latest (Nov 20, 2026), Wccftech (Nov 18, 2026), Guru3D, TechSpot: GeForce 621.14
  (Nov 4) and 621.24 (Nov 12). NVDisplay.Container.exe (NVIDIA Display Container LS) keeps
  rewriting C:\\ProgramData\\NVIDIA Corporation\\nvtopps\\nct\\nvlog.nvlgstg while idle.
  A forum user on 621.24: "about 30gb per 1h". On 621.14: 515 MB in 5 min idle; 621.01: under 2 MB.
- Wear: Windows Latest (citing Tom's Hardware): a 1 TB SSD rated ~600 TB written; 30 GB/h for
  8 h a day is ~15% of that a year (30*8*365 = 87.6 TB = 14.6%). Won't kill a drive quickly.
- Fix: GeForce Hotfix 621.35 (Wccftech, Nov 21, 2026) "to resolve the issue". Hotfixes are
  "beta, optional, and provided as-is" (Nvidia, quoted by Wccftech). Rollback to 621.01 also cited.
- Check: Resource Monitor > Disk > sort by Write (Windows Latest, Wccftech).
Build: python -m studio.make videos/2026-11-22-driver-ssd-writes
"""
import math

from studio import *

VIDEO = Video("driver-ssd-writes", format="short", speed=1.08,
              question="What did Resource Monitor show on your PC?")

SSD = BLUE


def ssd(c, cx, cy, w=420, h=150, alpha=1.0, glow=0.0, label="SSD"):
    """An M.2 stick: green PCB, a controller and four NAND packages."""
    x, y = cx - w / 2, cy - h / 2
    if glow > 0:
        rect(c, x - 6, y - 6, w + 12, h + 12, fill=SSD, radius=14, alpha=alpha * 0.35 * glow, blur=18)
    rect(c, x, y, w, h, fill="#17281C", stroke=GREEN, width=3, radius=10, alpha=alpha)
    # gold contact fingers on the left
    for i in range(7):
        rect(c, x + 6, y + 18 + i * 17, 18, 10, fill=GOLD, radius=2, alpha=alpha * 0.9)
    rect(c, x + 44, y + 35, 70, 80, fill="#2A2F38", radius=6, alpha=alpha)
    for i in range(4):
        rect(c, x + 135 + i * (w - 160) / 4, y + 28, (w - 160) / 4 - 14, h - 56, fill="#232831",
             stroke=SSD, width=2, radius=6, alpha=alpha)
    if label:
        text(c, label, cx, y + h + 40, size=38, color=SSD, weight="extrabold", alpha=alpha)


def monitor(c, cx, cy, w=360, h=230, alpha=1.0):
    rect(c, cx - w / 2, cy - h / 2, w, h, fill="#141922", stroke=GREY, width=4, radius=14, alpha=alpha)
    rect(c, cx - 14, cy + h / 2, 28, 50, fill=GREY, alpha=alpha)
    rect(c, cx - 80, cy + h / 2 + 46, 160, 12, fill=GREY, radius=6, alpha=alpha)


# ------------------------------------------------------------------ 1. hook
@VIDEO.scene("hook", lines=[
    Line("Your PC was doing nothing.", show="Your PC was doing nothing."),
    Line("Your SSD was writing thirty gigabytes an hour.", show="Your SSD was writing 30 GB an hour."),
    Line("That's what users measured on two new Nvidia drivers."),
], pad_in=0.1, sfx=[("whoosh", 0.0), ("pop", "nothing"), ("riser", ("thirty", -0.5)), ("hit", "hour"),
                    ("tick", "users")])
def hook(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    a = f.p(0.0, 0.4, "out")
    my = f.top + 190
    monitor(c, f.cx, my, alpha=a)
    if f.after("nothing"):
        z = f.since("nothing")
        for i in range(3):
            ph = (z * 0.6 + i / 3) % 1
            text(c, "z", f.cx + 40 + ph * 90 + i * 8, my - 10 - ph * 120, size=40 + i * 12, color=GREY,
                 weight="bold", alpha=(1 - ph) * a)
        text(c, "idle", f.cx - 60, my, size=56, color=GREY, weight="extrabold", alpha=f.p("nothing", 0.4))
    s = f.p("ssd", 0.5, "out")
    sy = f.top + 560
    w = f.p("writing", 0.4)
    ssd(c, f.cx, sy, alpha=s, glow=w * (0.6 + 0.4 * math.sin(f.t * 12)))
    if w > 0:
        # write packets streaming down from the PC into the SSD
        for i in range(6):
            ph = (f.t * 1.8 + i / 6) % 1
            rect(c, f.cx - 16, my + 180 + ph * 150, 32, 20, fill=GOLD, radius=4, alpha=w * (1 - ph * 0.6))
    n = f.p(("thirty", -0.1), 1.0, "out")
    if n > 0:
        number(c, lerp(0, 30, n), f.cx, f.top + 840, fmt="{:.0f} GB", size=200, color=GOLD)
        text(c, "every hour", f.cx, f.top + 970, size=56, color=WHITE, weight="extrabold", alpha=n)
    u = f.p("users", 0.5, "overshoot")
    if u > 0:
        with moved(c, scale=max(u, 0.001), about=(f.cx, f.top + 1080)):
            box(c, f.cx, f.top + 1080, 960, 96, fill="#161B23", stroke=GREY, width=3, radius=48)
            text(c, "user measurements · drivers 621.14 and 621.24", f.cx, f.top + 1080, size=34,
                 color=WHITE, weight="bold")


# ------------------------------------------------------------------ 2. the rewrite loop
@VIDEO.scene("rewrite", lines=[
    Line("The culprit: a background service, N V Display Container,",
         show="The culprit: a background service, NVDisplay.Container,"),
    Line("rewriting one log file, over and over."),
], sfx=[("pop", "culprit"), ("tick", "service"), ("whoosh", "rewriting"), ("tick", "over"),
        ("tick", ("over", 0.5))])
def rewrite(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    k = f.p("service", 0.5, "overshoot")
    if k > 0:
        with moved(c, scale=max(k, 0.001), about=(f.cx, f.top + 110)):
            box(c, f.cx, f.top + 110, 720, 120, fill="#161B23", stroke=PURPLE, width=4, radius=22)
            text(c, "NVDisplay.Container.exe", f.cx, f.top + 110, size=50, color=PURPLE, weight="extrabold")
    fx, fy, fw, fh = 240, f.top + 330, 600, 420
    a = f.p("log", 0.5)
    if a > 0:
        rect(c, fx, fy, fw, fh, fill="#141922", stroke=WHITE, width=3, radius=16, alpha=a)
        text(c, "nvlog.nvlgstg", fx + fw / 2, fy - 36, size=40, color=WHITE, weight="bold", alpha=a)
        arrow(c, f.cx, f.top + 175, f.cx, fy - 70, color=PURPLE, width=5, progress=a)
    r = f.since("rewriting") if f.after("rewriting") else -1
    total = 0.0
    if r >= 0:
        cycle = 1.1
        ph = (r % cycle) / cycle
        loops = int(r // cycle)
        rows = int(ph * 9)
        flash = 1 - clamp(ph * 6)
        for i in range(rows):
            rect(c, fx + 30, fy + 30 + i * 42, (fw - 60) * (0.55 + 0.4 * ((i * 37) % 10) / 10), 22,
                 fill=GOLD, radius=4, alpha=0.85)
        if loops > 0 and flash > 0:
            rect(c, fx, fy, fw, fh, fill=RED, radius=16, alpha=0.35 * flash)
            text(c, "erase · write again", f.cx, fy + fh / 2, size=48, color=RED, weight="extrabold", alpha=flash)
        total = r * 0.5 + loops * 0.3
        text(c, f"rewritten {loops + 1}×", f.cx, fy + fh + 60, size=48, color=GOLD, weight="extrabold")
    ssd(c, f.cx, f.top + 1060, w=380, h=130, alpha=f.p("rewriting", 0.4), glow=clamp(total))


# ------------------------------------------------------------------ 3. measured
@VIDEO.scene("measured", lines=[
    Line("One user logged five hundred megabytes in five idle minutes.",
         show="One user logged 515 MB in five idle minutes."),
    Line("The older driver? Under two.", show="The older driver? Under 2 MB."),
], sfx=[("whoosh", 0.0), ("riser", ("five", -0.4)), ("hit", "minutes"), ("pop", "two")])
def measured(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    text(c, "writes in 5 minutes at idle", f.cx, f.top + 40, size=44, color=WHITE, weight="extrabold",
         alpha=f.p(0.0, 0.4))
    base = f.top + 900
    line(c, 120, base, 960, base, color=GREY, width=3, alpha=f.p(0.0, 0.4))
    k = f.p(("five", -0.1), 1.2, "out")
    if k > 0:
        h = 680 * k
        bar(c, 330, base, 250, h, color=RED, progress=1.0)
        number(c, 515 * k, 330, base - h - 60, fmt="{:.0f} MB", size=80, color=RED)
        text(c, "621.14", 330, base + 50, size=48, color=WHITE, weight="extrabold")
    o = f.p("older", 0.5, "out")
    if o > 0:
        h = 680 * 2 / 515
        rect(c, 625, base - h, 250, h, fill=GREEN, radius=4, alpha=o)
        text(c, "< 2 MB", 750, base - 70, size=80, color=GREEN, weight="extrabold", alpha=o)
        text(c, "621.01", 750, base + 50, size=48, color=WHITE, weight="extrabold", alpha=o)
    t = f.p("two", 0.5, "overshoot")
    if t > 0:
        with moved(c, scale=max(t, 0.001), about=(f.cx, f.top + 1070)):
            text(c, "over 250× more", f.cx, f.top + 1070, size=64, color=GOLD, weight="extrabold", glow=6)


# ------------------------------------------------------------------ 4. wear
@VIDEO.scene("wear", lines=[
    Line("And SSDs wear out by writing."),
    Line("A typical one terabyte drive is rated for six hundred terabytes.",
         show="A typical 1 TB drive is rated for 600 TB written."),
    Line("Thirty an hour, eight hours a day, is fifteen percent of that a year.",
         show="30 GB an hour, 8 hours a day, is 15% of that a year."),
], sfx=[("pop", "wear"), ("whoosh", "rated"), ("tick", "eight"), ("riser", ("fifteen", -0.5)),
        ("hit", "year")])
def wear(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    # NAND cell: each write chips away at it
    a = f.p("wear", 0.5)
    cx, cy = f.cx, f.top + 170
    if a > 0:
        hits = int(clamp(f.since("wear") / 1.2) * 8) if f.after("wear") else 0
        for i in range(8):
            col = DIM if i < hits else SSD
            rect(c, cx - 300 + i * 76, cy - 50, 64, 100, fill=col, radius=8, alpha=a)
        text(c, "every write wears the flash a little", cx, cy + 100, size=36, color=GREY, weight="bold", alpha=a)
    # endurance tank
    tx, ty, tw, th = 160, f.top + 420, 760, 120
    r = f.p("rated", 0.5)
    if r > 0:
        rect(c, tx, ty, tw, th, stroke=WHITE, width=4, radius=20, alpha=r)
        text(c, "1 TB SSD · ~600 TB written rating", f.cx, ty - 40, size=40, color=WHITE, weight="bold", alpha=r)
    u = f.p(("fifteen", -0.2), 1.2, "out")
    if u > 0:
        rect(c, tx + 6, ty + 6, (tw - 12) * 0.146 * u, th - 12, fill=RED, radius=16)
        number(c, 15 * u, f.cx, ty + 270, fmt="{:.0f}% a year", size=130, color=RED)
    e = f.p("eight", 0.5)
    if e > 0:
        runs(c, [("30 GB/h", GOLD), (" × ", GREY), ("8 h", GOLD), (" × ", GREY), ("365", GOLD),
                 (" ≈ 88 TB", WHITE)], f.cx, f.top + 900, size=52, weight="extrabold")
        text(c, "if you leave the PC on, idle", f.cx, f.top + 980, size=36, color=GREY, weight="medium", alpha=e)
    text(c, "won't kill a drive overnight, but it's wasted life", f.cx, f.top + 1100, size=36, color=WHITE,
         weight="bold", alpha=f.p("year", 0.6))


# ------------------------------------------------------------------ 5. the fix
VERS = [("621.01", GREEN, "ok"), ("621.14", RED, "bug"), ("621.24", RED, "bug"), ("621.35", GOLD, "hotfix")]


@VIDEO.scene("fix", lines=[
    Line("Nvidia's hotfix six twenty-one thirty-five, out November twenty-first, addresses it.",
         show="Nvidia's hotfix 621.35, out Nov 21, addresses it."),
    Line("It's an optional beta. Or roll back to six twenty-one oh one.",
         show="It's an optional beta. Or roll back to 621.01."),
], sfx=[("whoosh", 0.0), ("pop", "hotfix"), ("ding", "addresses"), ("tick", "optional"), ("pop", "roll")])
def fix(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    for i, (v, col, tag) in enumerate(VERS):
        cue = (0.0, 0.25 * i) if i < 3 else "hotfix"
        k = f.p(cue if i == 3 else 0.15 + 0.25 * i, 0.5, "overshoot")
        if k <= 0:
            continue
        y = f.top + 120 + i * 230
        hl = (i == 3 and f.after("addresses")) or (i == 0 and f.after("roll"))
        with moved(c, scale=max(k, 0.001), about=(f.cx, y)):
            box(c, f.cx, y, 760, 170, fill="#161B23", stroke=col, width=7 if hl else 4, radius=26)
            text(c, v, f.cx - 200, y, size=72, color=WHITE, weight="extrabold")
            text(c, tag, f.cx + 210, y, size=56, color=col, weight="extrabold")
    o = f.p("optional", 0.5)
    if o > 0:
        text(c, "hotfixes: beta, optional, \"as-is\"", f.cx, f.top + 1060, size=40, color=GREY, weight="bold",
             alpha=o)


# ------------------------------------------------------------------ 6. check yours
ROWS = [("NVDisplay.Container.exe", "8,410,112", RED), ("System", "96,220", GREY),
        ("MsMpEng.exe", "41,004", GREY), ("chrome.exe", "18,560", GREY)]


@VIDEO.scene("check", lines=[
    Line("Check yours: open Resource Monitor, Disk tab, and sort by Write.",
         show="Check yours: open Resource Monitor, Disk tab, sort by Write."),
], sfx=[("pop", "check"), ("tick", "disk"), ("whoosh", "sort"), ("ding", "write")], pad_out=0.6)
def check(f):
    c = f.c
    grid(c, f.W, f.H, top=f.top, bottom=f.bottom)
    a = f.p("resource", 0.5)
    x0, y0, w = 90, f.top + 160, 900
    if a > 0:
        rect(c, x0, y0, w, 760, fill="#141922", stroke=GREY, width=3, radius=16, alpha=a)
        text(c, "Resource Monitor", x0 + 30, y0 + 50, size=40, color=WHITE, weight="bold", align="left", alpha=a)
    d = f.p("disk", 0.4)
    if d > 0:
        for j, tab in enumerate(["CPU", "Memory", "Disk", "Network"]):
            col = GOLD if tab == "Disk" else GREY
            text(c, tab, x0 + 70 + j * 200, y0 + 130, size=36, color=col,
                 weight="extrabold" if tab == "Disk" else "medium", alpha=d)
        line(c, x0 + 400, y0 + 158, x0 + 480, y0 + 158, color=GOLD, width=5, alpha=d)
        text(c, "Process", x0 + 40, y0 + 220, size=32, color=GREY, weight="bold", align="left", alpha=d)
        text(c, "Write (B/sec)", x0 + w - 40, y0 + 220, size=32,
             color=GOLD if f.after("write") else GREY, weight="bold", align="right", alpha=d)
    s = f.p("sort", 0.7)
    if d > 0:
        order = [1, 2, 0, 3]   # before sorting the culprit sits third
        for idx, (name, val, col) in enumerate(ROWS):
            before = order.index(idx)
            yy = y0 + 300 + lerp(before, idx, s) * 110
            rect(c, x0 + 20, yy - 40, w - 40, 80, fill="#2A1715" if idx == 0 and s > 0.9 else "#181E28",
                 radius=10, alpha=d)
            text(c, name, x0 + 40, yy, size=36, color=RED if idx == 0 else WHITE, weight="bold", align="left", alpha=d)
            text(c, val, x0 + w - 40, yy, size=36, color=col if idx == 0 else GREY, weight="bold", align="right",
                 alpha=d)
    text(c, "example numbers", f.cx, y0 + 820, size=30, color=GREY, weight="medium", alpha=d)
