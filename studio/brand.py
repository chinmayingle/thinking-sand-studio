"""Brand constants for The Thinking Sand (see the CC project doc claude/channel-branding.md)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "assets" / "fonts"
MODELS = ROOT / "models"

# Colours. Gold and blue are manim's YELLOW_D and BLUE_C, so diagrams read like 3Blue1Brown.
BG = "#0E1116"
GOLD = "#F4D345"   # sand gold: money, the key number, the spoken caption word
BLUE = "#58C4DD"   # core blue: the thing being explained, annotations
WHITE = "#ECEFF4"
GREY = "#8B93A1"
DIM = "#2B313C"
RED = "#FC6255"
GREEN = "#83C167"
TEAL = "#5CD0B3"
PURPLE = "#9A72AC"
SAND = ["#F3E2B3", "#E3C88A", "#C79D57", "#B78A49"]

NAME = "The Thinking Sand"
HANDLE = "@TheThinkingSand"

FPS = 30

# picture: the vertical band the main picture should stay inside.
# Shorts: the YouTube interface covers the bottom; captions sit at caption_y, clear of it.
FORMATS = {
    "short": dict(W=1080, H=1920, picture=(230, 1360), caption_y=1500),
    "long": dict(W=1920, H=1080, picture=(0, 1080), caption_y=None),
}

# Narrator voice used by every video so far (Kokoro, Apache-2.0).
VOICE = "af_heart"
SPEED = 1.03
