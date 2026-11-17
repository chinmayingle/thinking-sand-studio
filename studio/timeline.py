"""Videos, scenes, lines and the frame object every scene draws with.

A video is a list of scenes. Each scene owns the narration lines spoken over it,
so its length comes from the voice. A scene is a function of time: it gets a
Frame and draws that one moment. Cues tie the picture to the words:
f.p("cores") is the eased progress of a move that starts when "cores" is spoken.
"""
from dataclasses import dataclass, field

from .brand import FORMATS, FPS, VOICE, SPEED
from .ease import EASES, clamp
from .voice import clean, synth


@dataclass
class Line:
    say: str                 # what the voice reads (respelled for the engine where needed)
    show: str = None         # caption text if it differs ("fifty-ninety" spoken, "5090" shown)
    pause: float = 0.22      # silence after the line, seconds
    voice: str = None
    speed: float = None


@dataclass
class SceneDef:
    name: str
    fn: callable
    lines: list
    pad_in: float = 0.25
    pad_out: float = 0.35
    min_dur: float = 0.0
    fade: bool = True
    sfx: list = field(default_factory=list)   # [(name, when)] or [(name, when, gain_db)]; when = seconds,
                                               # a cue phrase, or (phrase, offset)
    music: bool = True
    captions: bool = True                      # Shorts only: burn in captions over this scene


@dataclass
class PlannedLine:
    line: Line
    start: float             # global seconds
    end: float
    audio: object            # float32 at 24 kHz
    words: list              # [(spoken word, start, end)] in global seconds
    shown: list              # [(caption word, start, end)] in global seconds


@dataclass
class PlannedScene:
    index: int
    d: SceneDef
    start: float
    dur: float
    lines: list

    @property
    def name(self):
        return self.d.name

    @property
    def frames(self):
        return round(self.dur * FPS)


class Video:
    def __init__(self, slug, format="short", voice=VOICE, speed=SPEED, question=None,
                 endcard=True, endcard_lines=None):
        assert format in FORMATS, format
        self.slug, self.format = slug, format
        self.voice, self.speed = voice, speed
        self.question = question
        self.endcard, self.endcard_lines = endcard, endcard_lines
        self.scenes = []
        f = FORMATS[format]
        self.W, self.H = f["W"], f["H"]
        self.picture, self.caption_y = f["picture"], f["caption_y"]

    def scene(self, name, lines=(), **kw):
        """Decorator: @VIDEO.scene("hook", lines=[Line("..."), ...], sfx=[("whoosh", "cores")])."""
        def deco(fn):
            self.scenes.append(SceneDef(name, fn, [l if isinstance(l, Line) else Line(l) for l in lines], **kw))
            return fn
        return deco

    def all_scenes(self):
        scenes = list(self.scenes)
        if self.endcard:
            from .endcard import endcard_scene
            scenes.append(endcard_scene(self))
        return scenes

    def plan(self, cache_dir, only=None):
        """Record every line (cached) and lay the scenes end to end."""
        out, t = [], 0.0
        for i, d in enumerate(self.all_scenes()):
            start, cur, planned = t, t + d.pad_in, []
            for ln in d.lines:
                audio, words = synth(ln.say, ln.voice or self.voice, ln.speed or self.speed, cache_dir)
                dur = len(audio) / 24000
                gw = [(w, cur + s, cur + e) for (w, s, e) in words]
                planned.append(PlannedLine(ln, cur, cur + dur, audio, gw, _shown(ln, gw)))
                cur += dur + ln.pause
            if d.lines:
                cur -= d.lines[-1].pause
            dur = max(cur + d.pad_out - start, d.min_dur)
            dur = round(dur * FPS) / FPS
            out.append(PlannedScene(i, d, start, dur, planned))
            t = start + dur
        return out


def _shown(line, gw):
    """Caption words with times. When the caption text differs from the spoken text,
    caption words are spread across the spoken words' times in order."""
    if not line.show:
        return list(gw)
    sw, n = line.show.split(), len(gw)
    if not sw or not n:
        return []
    out = []
    for j, w in enumerate(sw):
        a = min(n - 1, int(j * n / len(sw)))
        b = max(a, min(n - 1, int((j + 1) * n / len(sw)) - 1))
        out.append((w, gw[a][1], gw[b][2]))
    return out


class Frame:
    """What a scene function receives for one frame.

    f.c          the Skia canvas          f.W, f.H     frame size
    f.t          seconds into the scene   f.T          seconds into the video
    f.dur        scene length             f.cx, f.cy   centre of the picture area
    f.top, f.bottom  the picture band (Shorts keep clear of captions and the interface)
    """

    def __init__(self, video, scene, canvas, t):
        self.video, self.scene, self.c = video, scene, canvas
        self.W, self.H = video.W, video.H
        self.t, self.T, self.dur = t, scene.start + t, scene.dur
        self.top, self.bottom = video.picture
        self.cx, self.cy = self.W / 2, (self.top + self.bottom) / 2

    # ---- cues: times (scene-relative) when words are spoken
    def _find(self, phrase, nth=1):
        target = [clean(w) for w in phrase.split()]
        words = [(clean(w), s, e) for pl in self.scene.lines for (w, s, e) in pl.words]
        hits = 0
        for i in range(len(words) - len(target) + 1):
            if [w for w, _, _ in words[i:i + len(target)]] == target:
                hits += 1
                if hits == nth:
                    return words[i][1] - self.scene.start, words[i + len(target) - 1][2] - self.scene.start
        spoken = " ".join(w for w, _, _ in words)
        raise KeyError(f"cue {phrase!r} not spoken in scene {self.scene.name!r}: {spoken}")

    def cue(self, phrase, nth=1):
        """When `phrase` starts being spoken in this scene (seconds into the scene)."""
        return self._find(phrase, nth)[0]

    def cue_end(self, phrase, nth=1):
        return self._find(phrase, nth)[1]

    def line_start(self, i):
        return self.scene.lines[i].start - self.scene.start

    def line_end(self, i):
        return self.scene.lines[i].end - self.scene.start

    def _when(self, start):
        if isinstance(start, str):
            return self.cue(start)
        if isinstance(start, tuple):          # ("cores", 0.3): 0.3 s after "cores"
            return self.cue(start[0]) + start[1]
        return float(start)

    def p(self, start, dur=0.6, ease="smooth"):
        """Eased progress 0..1 of a move that starts at `start` (seconds, or a cue phrase,
        or (phrase, offset)) and lasts `dur` seconds."""
        s = self._when(start)
        x = 1.0 if dur <= 0 else (self.t - s) / dur
        return EASES[ease](clamp(x))

    def after(self, start):
        return self.t >= self._when(start)

    def since(self, start):
        return max(0.0, self.t - self._when(start))

    def spoken_word(self):
        """The word being said right now (caption text), or None."""
        for pl in self.scene.lines:
            for (w, s, e) in pl.shown:
                if s <= self.T < e:
                    return w
        return None
