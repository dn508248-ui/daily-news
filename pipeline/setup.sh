#!/usr/bin/env bash
# One-time setup per (fresh) machine: Python packages + Kokoro voice model (~350 MB, cached).
set -e
pip install -q --break-system-packages kokoro-onnx soundfile scipy 2>/dev/null || pip install -q kokoro-onnx soundfile scipy
M="${DN_MODELS:-$HOME/.cache/daily-news/models}"
mkdir -p "$M"
U=https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0
[ -s "$M/kokoro-v1.0.onnx" ] || curl -sSL -o "$M/kokoro-v1.0.onnx" "$U/kokoro-v1.0.onnx"
[ -s "$M/voices-v1.0.bin" ] || curl -sSL -o "$M/voices-v1.0.bin" "$U/voices-v1.0.bin"
python3 -c "import playwright, kokoro_onnx, scipy" && which ffmpeg >/dev/null && echo "setup ok"
