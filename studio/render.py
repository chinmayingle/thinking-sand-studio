"""Drawing frames and encoding them.

One encoded file per scene, all with identical settings, joined with the concat
demuxer and stream copy; sound is added with -c:v copy (see the video-making skill).
Film grain is added at encode time. Each scene is written to a temporary .mp4 name
and renamed only when ffmpeg exits 0, so a stopped render never leaves a short file.
"""
import os
import subprocess
from pathlib import Path

import numpy as np
import skia

from .brand import BG, FPS
from .captions import draw_caption
from .draw import rgba
from .timeline import Frame

X264 = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p",
        "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709"]
# Light temporal grain on luma: dithers gradients against banding. Stronger grain survives
# x264 at CRF 19 but costs ~150 MB a minute (tested Nov 17), so it stays subtle.
VF = "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p,noise=c0s=4:c0f=t+u"


def draw_frame(video, scene, canvas, t, cks):
    canvas.clear(rgba(BG))
    f = Frame(video, scene, canvas, t)
    scene.d.fn(f)
    if scene.d.captions and cks is not None:
        draw_caption(canvas, video, cks, f.T)
    if scene.d.fade:  # fade through the background at both ends, so any scene can be re-rendered alone
        k = min(1.0, t / 0.2, max(0.0, (scene.dur - t - 1 / FPS) / 0.2))
        if k < 1.0:
            canvas.drawRect(skia.Rect.MakeWH(video.W, video.H), skia.Paint(Color=rgba(BG, 1 - k)))


def render_scene(video, scene, out_path, cks):
    out_path = Path(out_path)
    tmp = out_path.with_name(out_path.stem + ".part.mp4")
    buf = np.zeros((video.H, video.W, 4), np.uint8)
    surf = skia.Surface(buf)
    canvas = surf.getCanvas()
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba",
           "-s", f"{video.W}x{video.H}", "-r", str(FPS), "-i", "-", "-vf", VF, *X264, "-r", str(FPS),
           "-movflags", "+faststart", str(tmp)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    try:
        for i in range(scene.frames):
            draw_frame(video, scene, canvas, i / FPS, cks)
            proc.stdin.write(buf.tobytes())
        proc.stdin.close()
        if proc.wait() != 0:
            raise RuntimeError(f"ffmpeg failed on scene {scene.name}")
    except BaseException:
        proc.kill()
        raise
    os.replace(tmp, out_path)
    return out_path


def still(video, plan, T, path, cks):
    """One full-size PNG of the moment T seconds into the video."""
    for sc in plan:
        if sc.start <= T < sc.start + sc.dur:
            break
    else:
        sc = plan[-1]
    buf = np.zeros((video.H, video.W, 4), np.uint8)
    surf = skia.Surface(buf)
    draw_frame(video, sc, surf.getCanvas(), max(0.0, min(T - sc.start, sc.dur - 1 / FPS)), cks)
    surf.makeImageSnapshot().save(str(path), skia.kPNG)
    return path


def concat(files, out_path):
    lst = Path(out_path).with_suffix(".txt")
    lst.write_text("".join(f"file '{Path(f).resolve()}'\n" for f in files))
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0",
                    "-i", str(lst), "-c", "copy", str(out_path)], check=True)


def mux(video_path, audio_path, out_path):
    tmp = Path(out_path).with_name(Path(out_path).stem + ".part.mp4")
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(video_path),
                    "-i", str(audio_path), "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac",
                    "-b:a", "192k", "-ar", "48000", "-shortest", "-movflags", "+faststart", str(tmp)], check=True)
    os.replace(tmp, out_path)
