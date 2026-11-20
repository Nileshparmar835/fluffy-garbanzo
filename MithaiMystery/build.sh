#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
mode="${1:-full}"
bash setup.sh "$mode"
py="$(cat .runtime/python-path)"
if [[ "$mode" == art ]]; then
    "$py" src/art.py
    exit
fi
if [[ "$mode" == full ]]; then
    "$py" src/voice.py
    "$py" src/align_words.py
fi
"$py" src/voice_preview.py
"$py" src/render.py --preview
"$py" src/render.py
"$py" src/verify.py
