# The Thinking Sand: studio

**Status: READY** (engine v1, Nov 17 2026). Scheduled runs: use this repo for every video.

Code for making the channel's videos: 3Blue1Brown-style vector animation (Skia), narration
with exact word timings (Kokoro TTS), burnt-in captions for Shorts, synthesized music and
effects, and the standard end card with the etched-grain logo. One command builds a
finished MP4, its .srt captions and a contact sheet to check.

Channel rules live in the CC project docs (`claude/video-rules.md`, `claude/channel-branding.md`).
This repo encodes the parts that are code: brand colours, fonts, the end card, loudness.

## Quick start (fresh workspace)

```bash
bash setup.sh                                    # ~1-2 min: packages + voice model (checked, then patched for timings)
python -m studio.make videos/_example --plan     # record the voice, print the timeline with word times
python -m studio.make videos/_example --stills 2.6,9.7,24.2   # full-size PNGs of chosen moments
python -m studio.make videos/_example            # full render, ~40 s for this 25 s Short on 2 cores
```

Outputs go to `videos/<folder>/out/` (git-ignored): `<slug>.mp4`, `<slug>.srt`, `contact.jpg`,
`report.json` (duration, loudness, true peak, scene joins, warnings), `stills/`.

## Making a new video

1. `cp -r videos/_example videos/<YYYY-MM-DD>-<slug>` and rewrite `video.py` (script + scenes)
   and `upload.md` (title, description, tags, pinned comment, sources).
2. `python -m studio.make videos/<folder> --plan`: check the length (Shorts 40-58 s) and the word times.
3. `--stills` at the busiest moments; look at them at full size before the full render.
4. Full render. Read `report.json`: no warnings, about -14 LUFS, true peak at or below -1 dB.
   Look at `contact.jpg`. Re-render one scene with `--only <scene>`; new sound only with `--sound-only`.
5. Deliver `out/<slug>.mp4`, `out/<slug>.srt` and `upload.md`. Never upload to YouTube from a run.
6. Commit the folder (video.py, upload.md; `out/` is ignored) and push to `main`:
   `git add videos/<folder> && git commit -m "video: <slug>" && git push`.

## Writing video.py

```python
from studio import *

VIDEO = Video("rt-vram", format="short",           # "short" 1080x1920, "long" 1920x1080
              question="Would you turn ray tracing on now?")   # end-card comment question

@VIDEO.scene("hook", lines=[
    Line("Ray tracing just got ninety percent lighter on your V RAM.",   # what the voice says
         show="Ray tracing just got 90% lighter on your VRAM."),          # what the captions show
], sfx=[("whoosh", 0.0), ("hit", "ninety")])
def hook(f):
    k = f.p("ninety", 0.8, "out")                 # eased 0..1, starting when "ninety" is spoken
    number(f.c, lerp(0, 90, k), f.cx, f.cy, fmt="{:.0f}%", size=240)
```

- A scene's length comes from its lines (plus `pad_in`, `pad_out`, or `min_dur`). The end card
  is added automatically: the question, "Tell me in the comments", like/share/subscribe, the logo,
  "The Thinking Sand" and "@TheThinkingSand".
- Scenes fade through the background at both ends, so any scene can be re-rendered alone.
- Shorts: keep the picture between `f.top` and `f.bottom` (y 230-1360); captions sit at y 1500,
  three words at a time, the spoken word in gold.
- Cues match the spoken text (`say`), whole words, case-insensitive: `f.cue("eight and a half")`.

### Frame (`f`)
| | |
|---|---|
| `f.c` | Skia canvas |
| `f.t`, `f.T`, `f.dur` | seconds into the scene, into the video, scene length |
| `f.W`, `f.H`, `f.cx`, `f.cy`, `f.top`, `f.bottom` | frame size, centre and band of the picture area |
| `f.cue(phrase)`, `f.cue_end(phrase)` | when a phrase starts / ends being spoken (scene seconds) |
| `f.p(start, dur=0.6, ease="smooth")` | eased progress; `start` = seconds, a phrase, or `(phrase, offset)` |
| `f.after(start)`, `f.since(start)` | has it happened; seconds since |
| `f.line_start(i)`, `f.line_end(i)`, `f.spoken_word()` | line times; the caption word being said |

Eases: `smooth` (default), `out`, `in`, `overshoot`, `linear`, `there_and_back`; also `pulse(t)`.

### Drawing (all take the canvas first; colours are hex strings)
`text(c, s, x, y, size, color, weight, align, anchor, alpha, max_width, glow)`,
`runs(c, [(s, color), ...], x, y, size)` (one line in several colours), `typewriter(s, p)`,
`number(c, value, x, y, fmt, size)`, `rect`, `box` (centred rect), `circle`, `line`, `arrow`
(grows with `progress`), `brace(c, x1, x2, y, label)`, `polyline(pts)` + `stroke_path(c, path, progress=)`
(write-on strokes), `grid` (faint NumberPlane), `bar` (grows from a baseline, label + value),
`blocks` (grid of squares: cores, memory chips), `chip(c, cx, cy, size, color, label, glow)`,
`draw_logo(c, cx, cy, size, progress, glow)`, `vignette`, and `moved(c, dx, dy, scale, rotate,
about, alpha)` as a context manager for moving, scaling or fading a group.
Weights: regular, medium, semibold, bold, extrabold, italic, and math / math-italic / math-bold
(KaTeX fonts, for formulas).

### Sound
Effects by name in a scene's `sfx`: `whoosh`, `pop`, `tick`, `ding`, `hit`, `riser`, `swell`,
as `(name, when)` or `(name, when, gain_db)`. The music bed (D minor, 96 bpm) is synthesized,
sits about 17 dB under the voice and ducks while it speaks; `music=False` on a scene silences
it there. Everything is mastered to -14 LUFS, true peak at or below -1 dB. No licensed audio.

## Pronunciation (Kokoro)
Write `say` the way an engineer says it; put the written form in `show`.
- Model numbers: "5090" → "fifty-ninety", "4090" → "forty-ninety", "RTX 5090" → "R T X fifty-ninety".
- Spell out letters the engine misreads: "VRAM" → "V RAM" (as written it says "vram"),
  "FP8" → "F P eight", "IPO" → "I P O", "TSMC" → "T S M C", "LED" → "L E D".
- Fine as written (phonemes checked Nov 17): GPU, GPUs, CPU, AI, AMD (do not write "A M D"),
  SRAM ("ess-ram"), DLSS, GDDR7, PCIe, LLM, H100, cache, Nvidia, Cerebras, Groq, teraflops.
- Check unusual words before recording: `python -c "from studio.voice import kokoro; print(kokoro().tokenizer.phonemize('word'))"`.

## Layout
```
studio/      engine: brand, draw, ease, logo, voice, timeline, captions, audio, render, endcard, check, make
tools/       patch_kokoro.py (exposes the model's phoneme durations as an output)
assets/      fonts (Inter, OFL; KaTeX, MIT) and brand PNGs (logo-800.png, watermark-300.png)
videos/      one folder per video: video.py + upload.md (renders are not committed)
models/      downloaded by setup.sh (git-ignored)
```

Licences: Inter (SIL OFL 1.1) and KaTeX fonts (MIT) in `assets/fonts`; Kokoro-82M weights (Apache-2.0)
and kokoro-onnx (MIT) are downloaded at setup.
