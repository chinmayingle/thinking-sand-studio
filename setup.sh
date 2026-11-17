#!/usr/bin/env bash
# One-time setup in a fresh workspace (about 1-2 minutes): Python packages, the Kokoro
# voice model (downloaded from GitHub releases, checked, then patched to report word
# timings), and a smoke test. Safe to run again; finished steps are skipped.
set -euo pipefail
cd "$(dirname "$0")"

pip install --break-system-packages -q -r requirements.txt 2>&1 | grep -v -i "warning: running pip as" || true

command -v ffmpeg >/dev/null || { echo "ffmpeg is missing: apt-get install -y ffmpeg"; exit 1; }

mkdir -p models
REL=https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0
fetch() {  # name sha256
  if [ ! -f "models/$1" ]; then
    curl -sSL --retry 3 -o "models/$1.part" "$REL/$1"
    echo "$2  models/$1.part" | sha256sum -c --quiet - || { echo "checksum mismatch for $1"; rm -f "models/$1.part"; exit 1; }
    mv "models/$1.part" "models/$1"
  fi
}
fetch voices-v1.0.bin bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d
if [ ! -f models/kokoro-v1.0-timed.onnx ]; then
  fetch kokoro-v1.0.onnx 7d5df8ecf7d4b1878015a32686053fd0eebe2bc377234608764cc0ef3636a6c5
  python3 tools/patch_kokoro.py models/kokoro-v1.0.onnx models/kokoro-v1.0-timed.onnx
  rm -f models/kokoro-v1.0.onnx
fi

python3 - <<'EOF'
from studio.voice import kokoro
k = kokoro()
audio, sr, t = k.create_timed("Ready.", voice="af_heart")
assert t, "no word timings"
print(f"studio ready: voice ok ({len(audio)/sr:.2f}s test clip, {len(t)} timed phonemes)")
EOF
