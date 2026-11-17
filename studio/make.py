"""Build a video from its folder.

    python -m studio.make videos/<folder> --plan            # record the voice, print the timeline
    python -m studio.make videos/<folder> --stills 2.5,9,21 # full-size PNGs of chosen moments
    python -m studio.make videos/<folder>                   # full render + checks
    python -m studio.make videos/<folder> --only hook       # re-render one scene, then re-join

Outputs go to videos/<folder>/out/ (git-ignored): <slug>.mp4, <slug>.srt, contact.jpg, report.json.
"""
import argparse
import importlib.util
import json
import sys
import time
from pathlib import Path

import soundfile as sf

from . import audio, captions, check, render
from .brand import FPS
from .timeline import Frame


def load(folder):
    folder = Path(folder).resolve()
    spec = importlib.util.spec_from_file_location(f"video_{folder.name.replace('-', '_')}", folder / "video.py")
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(folder))
    spec.loader.exec_module(mod)
    return folder, mod.VIDEO


def sfx_events(video, plan):
    events = []
    for sc in plan:
        f = Frame(video, sc, None, 0.0)
        for item in sc.d.sfx:
            name, when = item[0], item[1]
            gain = item[2] if len(item) > 2 else 0.0
            try:
                events.append((sc.start + f._when(when), name, gain))
            except KeyError as e:
                print(f"warning: sfx {name!r} skipped: {e}")
    return events


def print_plan(plan):
    for sc in plan:
        print(f"[{sc.start:6.2f} +{sc.dur:5.2f}s] {sc.name}")
        for pl in sc.lines:
            ws = " ".join(f"{w}@{s - sc.start:.2f}" for w, s, _ in pl.words)
            print(f"      {pl.start - sc.start:5.2f}-{pl.end - sc.start:5.2f}  {ws}")
    print(f"total {plan[-1].start + plan[-1].dur:.2f}s")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--stills", default="")
    ap.add_argument("--only", default="", help="comma-separated scene names to re-render")
    ap.add_argument("--sound-only", action="store_true", help="keep rendered scenes, rebuild sound and mux")
    ap.add_argument("--no-music", action="store_true")
    a = ap.parse_args(argv)

    folder, video = load(a.folder)
    out = folder / "out"
    (out / "scenes").mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    plan = video.plan(out / "voice")
    total = plan[-1].start + plan[-1].dur
    cks = captions.chunks(plan) if video.caption_y is not None else None
    print(f"voice ready in {time.time() - t0:.1f}s, video {total:.2f}s")
    if a.plan:
        print_plan(plan)
        return
    if a.stills:
        (out / "stills").mkdir(exist_ok=True)
        for T in [float(x) for x in a.stills.split(",") if x]:
            p = render.still(video, plan, T, out / "stills" / f"t{T:06.2f}.png", cks)
            print("still", p)
        return

    files = [out / "scenes" / f"{sc.index:02d}_{sc.name}.mp4" for sc in plan]
    for sc, path in zip(plan, files):
        if (a.sound_only or (a.only and sc.name not in a.only.split(","))) and path.exists():
            continue
        t1 = time.time()
        render.render_scene(video, sc, path, cks)
        print(f"scene {sc.name}: {sc.frames} frames in {time.time() - t1:.1f}s")

    render.concat(files, out / "picture.mp4")
    mixwav, final_wav = out / "mix.wav", out / "final.wav"
    sf.write(mixwav, audio.mix(plan, total, sfx_events(video, plan), music=not a.no_music), audio.SR)
    audio.master(mixwav, final_wav)
    final = out / f"{video.slug}.mp4"
    render.mux(out / "picture.mp4", final_wav, final)
    (out / f"{video.slug}.srt").write_text(captions.srt(plan))

    dur = check.probe_duration(final)
    lufs, tp = check.loudness(final)
    jn = check.joins(files)
    check.contact_sheet(final, out / "contact.jpg")
    warnings = []
    if video.format == "short" and dur > 58.5:
        warnings.append(f"Short is {dur:.1f}s: keep it to 40-58 s, never over 60")
    if video.format == "short" and dur < 40:
        warnings.append(f"Short is {dur:.1f}s: aim for 40-58 s")
    if lufs is not None and abs(lufs + 14) > 1.0:
        warnings.append(f"loudness {lufs} LUFS, expected -14")
    if tp is not None and tp > -0.9:
        warnings.append(f"true peak {tp} dBFS, expected <= -1")
    for a_, b_, d in jn:
        if d is not None and d > 6:
            warnings.append(f"visible jump between {a_} and {b_} (diff {d:.1f})")
    report = {"file": str(final), "duration": dur, "frames_expected": round(total * FPS), "lufs": lufs,
              "true_peak": tp, "joins": jn, "warnings": warnings, "render_seconds": round(time.time() - t0, 1)}
    (out / "report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
