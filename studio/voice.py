"""Narration with Kokoro TTS and exact word timings.

setup.sh patches Kokoro's ONNX model to expose the duration of every phoneme
(tools/patch_kokoro.py), so each word's start and end come from the model itself,
not from guesses. One WAV per line, cached by text + voice + speed, so changing
one line only re-records that line.
"""
import hashlib
import json
import re
from pathlib import Path

import numpy as np
import soundfile as sf

from .brand import MODELS

PUNCT = ".,!?;:—–-\"'()“”‘’…"
_kokoro = None


def kokoro():
    global _kokoro
    if _kokoro is None:
        from kokoro_onnx import Kokoro
        model = MODELS / "kokoro-v1.0-timed.onnx"
        if not model.exists():
            raise FileNotFoundError(f"{model} missing: run setup.sh first")
        _kokoro = Kokoro(str(model), str(MODELS / "voices-v1.0.bin"))
        if not _kokoro.has_timings:
            raise RuntimeError("Kokoro model has no duration output: re-run tools/patch_kokoro.py")
    return _kokoro


def _phoneme_words(timings):
    """Group per-phoneme timings into space-separated words: [(phonemes, start, end)]."""
    out, cur, s, e = [], "", 0.0, 0.0
    for t in [*timings, None]:
        if t is not None and t.phoneme.strip():
            if not cur:
                s = t.start
            cur, e = cur + t.phoneme, t.end
            continue
        if cur:
            if cur.strip(PUNCT) == "" and out:   # lone punctuation joins the previous word
                ph, s0, _ = out[-1]
                out[-1] = (ph + cur, s0, e)
            else:
                out.append((cur, s, e))
        cur = ""
    return out


SKIP = set(" ˈˌːˑ" + PUNCT)


def _align(text_words, timings, lang="en-us"):
    """Map each written word to a time span by lining up phonemes, not word counts.

    The engine sometimes joins short words ("of that" -> one group) or splits one word
    into several, so word counts can't be trusted. Each written word is phonemized on
    its own, the results are joined, and that string is matched against the timed
    phonemes the model actually spoke (difflib). A word takes the times of its matched
    phonemes; a word with no match sits between its neighbours."""
    from difflib import SequenceMatcher
    if not text_words:
        return []
    spoken = [(t.phoneme, t.start, t.end) for t in timings if t.phoneme not in SKIP]
    S = "".join(p for p, _, _ in spoken)
    tok = kokoro().tokenizer
    Q, owner = "", []
    for i, w in enumerate(text_words):
        ph = "".join(ch for ch in tok.phonemize(w, lang) if ch not in SKIP)
        Q += ph
        owner += [i] * len(ph)
    spans = [[None, None] for _ in text_words]
    for a, b, size in SequenceMatcher(None, Q, S, autojunk=False).get_matching_blocks():
        for k in range(size):
            i, (_, s, e) = owner[a + k], spoken[b + k]
            lo, hi = spans[i]
            spans[i] = [s if lo is None else min(lo, s), e if hi is None else max(hi, e)]
    end_all = spoken[-1][2] if spoken else 0.0
    out = []
    for i, w in enumerate(text_words):
        s, e = spans[i]
        if s is None:
            prev_end = out[-1][2] if out else (spoken[0][1] if spoken else 0.0)
            nxt = next((spans[j][0] for j in range(i + 1, len(text_words)) if spans[j][0] is not None), end_all)
            s, e = prev_end, max(prev_end, nxt)
        out.append((w, s, e))
    for i in range(1, len(out)):  # keep words in order
        w, s, e = out[i]
        if s < out[i - 1][1]:
            out[i] = (w, out[i - 1][1], max(e, out[i - 1][1]))
    return out


def synth(text, voice, speed, cache_dir, lang="en-us"):
    """Speak one line. Returns (audio float32 at 24 kHz, words [(word, start, end)])."""
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha1(f"v3|{voice}|{speed}|{lang}|{text}".encode()).hexdigest()[:16]
    wav, meta = cache_dir / f"{key}.wav", cache_dir / f"{key}.json"
    if wav.exists() and meta.exists():
        audio, _ = sf.read(wav, dtype="float32")
        return audio, [tuple(w) for w in json.loads(meta.read_text())["words"]]
    audio, sr, timings = kokoro().create_timed(text, voice=voice, speed=speed, lang=lang)
    assert sr == 24000, sr
    words = _align(text.split(), timings, lang)
    sf.write(wav, audio, sr)
    meta.write_text(json.dumps({"text": text, "voice": voice, "speed": speed, "words": words}))
    return audio.astype(np.float32), words


def clean(word):
    """A word without surrounding punctuation, lower-cased, for cue matching."""
    return re.sub(r"^[^\w]+|[^\w]+$", "", word.lower())
