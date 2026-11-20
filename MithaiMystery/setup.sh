#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
mode="${1:-full}"
case "$mode" in full|existing-audio|art) ;; *) echo 'Use full, existing-audio or art.' >&2; exit 2;; esac
mkdir -p .runtime output
py="${PYTHON_BIN:-python3}"
command -v "$py" >/dev/null || { echo 'Python 3 is required.' >&2; exit 2; }
apt_install() {
    local admin=()
    if [[ "$(id -u)" != 0 ]]; then
        if command -v sudo >/dev/null && sudo -n true 2>/dev/null; then admin=(sudo -n)
        else echo "This sandbox needs the following system packages: $*. Use a sandbox where they are present or can be installed." >&2; return 2; fi
    fi
    command -v apt-get >/dev/null || { echo "Install the following packages in this Linux environment: $*" >&2; return 2; }
    "${admin[@]}" apt-get update
    "${admin[@]}" apt-get install -y "$@"
}
packages=()
if ! command -v ffmpeg >/dev/null || ! command -v ffprobe >/dev/null; then packages+=(ffmpeg); fi
if [[ "$mode" == art ]] && ! command -v inkscape >/dev/null; then packages+=(inkscape); fi
if ((${#packages[@]})); then apt_install "${packages[@]}"; fi
ready() {
    "$1" -c 'import numpy; from PIL import Image, ImageFont' >/dev/null 2>&1 || return 1
    if [[ "$mode" == full ]]; then
        "$1" -c 'from kokoro_onnx import Kokoro; import soundfile, onnxruntime; from importlib.metadata import version; assert version("kokoro-onnx")=="0.6.1"' >/dev/null 2>&1 || return 1
    fi
}
if ! ready "$py"; then
    if [[ ! -x .runtime/venv/bin/python ]]; then
        "$py" -m venv .runtime/venv || { apt_install python3-venv; "$py" -m venv .runtime/venv; }
    fi
    py="$PWD/.runtime/venv/bin/python"
    if ! ready "$py"; then
        if [[ "$mode" == full ]]; then "$py" -m pip install -r requirements.txt
        else "$py" -m pip install 'Pillow>=10,<14' 'numpy>=2.0.2,<3'; fi
    fi
fi
ready "$py"
ffmpeg -hide_banner -encoders > .runtime/encoders.txt 2>&1
grep -q libx264 .runtime/encoders.txt && grep -q ' aac ' .runtime/encoders.txt || { echo 'FFmpeg needs libx264 and AAC encoders.' >&2; exit 2; }
if [[ "$mode" == full ]]; then
    "$py" src/fetch_model.py
    "$py" src/check_voice.py
fi
printf '%s\n' "$(command -v "$py")" > .runtime/python-path
echo "Setup passed ($mode)."
