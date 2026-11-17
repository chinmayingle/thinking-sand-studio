"""Checks after a render: length, loudness, scene joins, and a contact sheet to look at."""
import re
import subprocess

import numpy as np


def probe_duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                          str(path)], capture_output=True, text=True, check=True).stdout
    return float(out.strip())


def loudness(path):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "ebur128=peak=true",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    tail = err[err.rfind("Summary:"):]
    i = re.search(r"I:\s+(-?[\d.]+) LUFS", tail)
    tp = re.search(r"Peak:\s+(-?[\d.]+) dBFS", tail)
    return (float(i.group(1)) if i else None, float(tp.group(1)) if tp else None)


def _gray(path, at_end):
    seek = ["-sseof", "-0.04"] if at_end else ["-ss", "0"]
    raw = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", *seek, "-i", str(path), "-frames:v", "1",
                          "-vf", "scale=96:-2,format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).astype(np.float32)


def joins(files):
    """Mean difference (0-255) between the last frame of each scene and the first of the next.
    Scenes fade through the background, so anything above ~6 is a visible jump."""
    out = []
    for a, b in zip(files, files[1:]):
        x, y = _gray(a, True), _gray(b, False)
        n = min(len(x), len(y))
        out.append((a.name, b.name, float(np.mean(np.abs(x[:n] - y[:n]))) if n else None))
    return out


def contact_sheet(path, out_jpg, cols=4, rows=3, width=320):
    dur = probe_duration(path)
    n = cols * rows
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(path), "-vf",
                    f"fps={n / dur:.5f},scale={width}:-2,tile={cols}x{rows}:padding=6:margin=6",
                    "-frames:v", "1", "-q:v", "3", str(out_jpg)], check=True)
    return out_jpg
