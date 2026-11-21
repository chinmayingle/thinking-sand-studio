"""Sound: a synthesized music bed in D minor, synthesized effects, voice ducking and mastering.

Nothing here is licensed audio: every sound is generated, so there are no claims.
Final loudness: -14 LUFS integrated, true peak held to -1 dBTP (ffmpeg loudnorm, two passes).
"""
import json
import re
import subprocess

import numpy as np
from scipy.signal import lfilter, resample_poly

SR = 48000
rng = np.random.default_rng(7)


def _t(dur):
    return np.arange(int(dur * SR)) / SR


def _onepole_lp(x, cutoff):
    a = 1 - np.exp(-2 * np.pi * cutoff / SR)
    return lfilter([a], [1, a - 1], x)


def _hp(x, cutoff):
    return x - _onepole_lp(x, cutoff)


def midi_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def _saw(freq, n, detune_cents=0.0):
    f = freq * 2 ** (detune_cents / 1200)
    ph = (np.arange(n) * f / SR + rng.random()) % 1.0
    return 2 * ph - 1


# ---------------------------------------------------------------- effects

def sfx(name):
    """Mono effect by name: whoosh, pop, tick, ding, hit, riser, swell."""
    if name == "whoosh":
        t = _t(0.5)
        env = np.sin(np.pi * np.clip(t / 0.5, 0, 1)) ** 2
        noise = rng.standard_normal(len(t))
        out = np.zeros_like(noise)
        segs = 12
        for i in range(segs):
            a, b = i * len(t) // segs, (i + 1) * len(t) // segs
            out[a:b] = _onepole_lp(noise[a:b], 400 + 3200 * i / segs)
        return (out * env * 0.5).astype(np.float32)
    if name == "pop":
        t = _t(0.1)
        f = 950 * np.exp(-t * 9)
        ph = 2 * np.pi * np.cumsum(f) / SR
        return (np.sin(ph) * np.exp(-t * 38) * 0.6).astype(np.float32)
    if name == "tick":
        t = _t(0.03)
        return (np.sin(2 * np.pi * 2200 * t) * np.exp(-t * 220) * 0.45).astype(np.float32)
    if name == "ding":
        t = _t(1.2)
        out = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t * d)
                  for f, a, d in ((1318.5, 0.5, 4.5), (2637 * 1.003, 0.22, 7), (3955 * 0.997, 0.1, 10)))
        return (out * 0.5).astype(np.float32)
    if name == "hit":
        t = _t(0.8)
        f = 40 + 60 * np.exp(-t * 14)
        body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 5)
        click = _onepole_lp(rng.standard_normal(len(t)), 900) * np.exp(-t * 60)
        return ((body + 0.5 * click) * 0.7).astype(np.float32)
    if name == "riser":
        t = _t(1.1)
        f = 180 * 2 ** (t / 1.1 * 2.5)
        tone = np.sin(2 * np.pi * np.cumsum(f) / SR)
        noise = _hp(rng.standard_normal(len(t)), 2000)
        env = (t / 1.1) ** 2
        return ((0.25 * tone + 0.35 * noise) * env * 0.6).astype(np.float32)
    if name == "swell":
        t = _t(1.6)
        env = np.sin(np.pi * t / 1.6) ** 2
        chord = sum(_saw(midi_hz(m), len(t), d) for m, d in ((62, -5), (65, 4), (69, 0)))
        return (_onepole_lp(chord, 900) * env * 0.12).astype(np.float32)
    raise KeyError(f"unknown sfx {name!r} (whoosh, pop, tick, ding, hit, riser, swell)")


# ---------------------------------------------------------------- music

def music_bed(duration, bpm=96):
    """Calm 4-chord loop in D minor (Dm, Bb, F, C): pad, bass, soft arpeggio, light pulse. Stereo."""
    n = int(duration * SR)
    beat = 60.0 / bpm
    bar = 4 * beat
    chords = [(50, (62, 65, 69)), (46, (62, 65, 70)), (41, (60, 65, 69)), (48, (60, 64, 67))]
    L, R = np.zeros(n), np.zeros(n)
    t_all = np.arange(n) / SR
    for k in range(int(duration / bar) + 2):
        root, triad = chords[k % 4]
        a = int(k * bar * SR)
        if a >= n:
            break
        b = min(n, int((k + 1) * bar * SR + 0.6 * SR))
        m = b - a
        tt = np.arange(m) / SR
        env = np.minimum(1, tt / 0.5) * np.minimum(1, np.maximum(0, (m / SR - tt) / 0.6))
        padL = sum(_saw(midi_hz(x), m, -6) for x in triad)
        padR = sum(_saw(midi_hz(x), m, +6) for x in triad)
        L[a:b] += _onepole_lp(padL, 1100) * env * 0.06
        R[a:b] += _onepole_lp(padR, 1100) * env * 0.06
        bass = np.sin(2 * np.pi * midi_hz(root - 12) * tt) * env * 0.16
        L[a:b] += bass
        R[a:b] += bass
        for i in range(8):  # eighth-note arpeggio
            s = a + int(i * beat / 2 * SR)
            if s >= n:
                break
            note = triad[i % 3] + (12 if i % 4 == 3 else 0)
            d = min(n - s, int(0.45 * SR))
            te = np.arange(d) / SR
            pl = np.sin(2 * np.pi * midi_hz(note + 12) * te) * np.exp(-te * 7) * 0.035
            (L if i % 2 == 0 else R)[s:s + d] += pl
            (R if i % 2 == 0 else L)[s:s + d] += pl * 0.4
        for i in range(4):  # soft pulse: kick on 1 and 3, hat on the off-beats
            s = a + int(i * beat * SR)
            if i in (0, 2) and s < n:
                d = min(n - s, int(0.25 * SR))
                te = np.arange(d) / SR
                kick = np.sin(2 * np.pi * np.cumsum(45 + 70 * np.exp(-te * 30)) / SR) * np.exp(-te * 14) * 0.12
                L[s:s + d] += kick
                R[s:s + d] += kick
            h = s + int(beat / 2 * SR)
            if h < n:
                d = min(n - h, int(0.05 * SR))
                te = np.arange(d) / SR
                hat = _hp(rng.standard_normal(d), 6000) * np.exp(-te * 80) * 0.025
                L[h:h + d] += hat
                R[h:h + d] += hat * 0.8
    fade = np.minimum(1, t_all / 1.5) * np.minimum(1, np.maximum(0, (duration - t_all) / 2.0))
    return np.stack([L * fade, R * fade], axis=1).astype(np.float32)


# ---------------------------------------------------------------- mix

def _envelope(x, win=0.04, attack=0.03, release=0.35):
    k = max(1, int(win * SR))
    rms = np.sqrt(np.convolve(x * x, np.ones(k) / k, mode="same"))
    a_up, a_dn = 1 - np.exp(-1 / (attack * SR)), 1 - np.exp(-1 / (release * SR))
    # Attack/release smoothing, decimated for speed and then interpolated back
    step = 48
    r = rms[::step]
    out = np.zeros_like(r)
    cur = 0.0
    for i, v in enumerate(r):
        a = 1 - (1 - a_up) ** step if v > cur else 1 - (1 - a_dn) ** step
        cur += a * (v - cur)
        out[i] = cur
    return np.interp(np.arange(len(x)), np.arange(len(out)) * step, out)


def mix(plan, duration, events, music=True, music_under_db=-17.0):
    """Voice + ducked music + effects, stereo float32 at 48 kHz.

    events: [(global seconds, sfx name, gain dB)]."""
    n = int(round(duration * SR))
    v24 = np.zeros(int(round(duration * 24000)) + 24000, np.float32)
    for sc in plan:
        for pl in sc.lines:
            s = int(round(pl.start * 24000))
            v24[s:s + len(pl.audio)] += pl.audio[: max(0, len(v24) - s)]
    voice = resample_poly(v24, 2, 1)[:n]
    if len(voice) < n:
        voice = np.pad(voice, (0, n - len(voice)))
    peak = np.max(np.abs(voice)) or 1.0
    voice = voice / peak * 0.5

    out = np.stack([voice, voice], axis=1)
    if music:
        bed = music_bed(duration)[:n]
        if len(bed) < n:  # music_bed truncates with int(), mix rounds: pad the last sample(s)
            bed = np.pad(bed, ((0, n - len(bed)),) + ((0, 0),) * (bed.ndim - 1))
        env = _envelope(voice)
        talking = env > 0.02
        v_rms = np.sqrt(np.mean(voice[talking] ** 2)) if talking.any() else 0.1
        b_rms = np.sqrt(np.mean(bed ** 2)) or 1.0
        bed *= v_rms * 10 ** (music_under_db / 20) / b_rms * 1.9   # level when not ducked
        duck = 1 - 0.47 * np.clip(env / (v_rms * 1.2), 0, 1)        # about -5.5 dB under speech
        for sc in plan:  # scenes that asked for no music
            if not sc.d.music:
                a, b = int(sc.start * SR), int((sc.start + sc.dur) * SR)
                duck[a:b] = 0.0
        out += bed * duck[:, None]
    for (t, name, gain_db) in events:
        fx = sfx(name) * 10 ** (gain_db / 20) * 0.5
        s = int(t * SR)
        if 0 <= s < n:
            e = min(n, s + len(fx))
            out[s:e] += fx[: e - s, None]
    return out.astype(np.float32)


def master(in_wav, out_wav, target=-14.0, tp=-1.8):
    """Two-pass EBU R128 loudness normalisation. The peak target leaves headroom for the
    AAC encode, which adds up to ~0.8 dB of inter-sample peak; the final file lands at <= -1 dBTP."""
    first = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", str(in_wav), "-af",
         f"loudnorm=I={target}:TP={tp}:LRA=11:print_format=json", "-f", "null", "-"],
        capture_output=True, text=True, check=True).stderr
    m = json.loads(re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", first, re.S).group(0))
    af = (f"loudnorm=I={target}:TP={tp}:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(in_wav), "-af", af,
                    "-ar", str(SR), "-c:a", "pcm_s24le", str(out_wav)], check=True)
